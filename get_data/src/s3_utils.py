from pathlib import Path
import re
import os
import boto3
from botocore import exceptions as boto3_exceptions
from tqdm import tqdm
import threading
import queue
import time

from conf.cluster_conf import ENV_VAR_FOR_AWS_USER_ID, ENV_VAR_FOR_AWS_USER_KEY
from utils import logger


log = logger.Logger().create(logger_name=__name__)


def is_valid_s3_key(name):
    if "valid" not in is_valid_s3_key.__dict__:  # check if it is the first call to this function
        is_valid_s3_key.valid_regex = r"[^a-zA-Z0-9!/\-_\*'\(\)]"
        is_valid_s3_key.exp = re.compile(is_valid_s3_key.valid_regex)
    res = is_valid_s3_key.exp.search(name)
    return (True, is_valid_s3_key.valid_regex) if res is None else (False, is_valid_s3_key.valid_regex)


def generate_valid_s3_key_from_str(name):
    if "valid" not in generate_valid_s3_key_from_str.__dict__:  # check if it is the first call to this function
        generate_valid_s3_key_from_str.valid_regex = r"[^a-zA-Z0-9!/\-_\*'\(\)]"
        generate_valid_s3_key_from_str.exp = re.compile(generate_valid_s3_key_from_str.valid_regex)
    return generate_valid_s3_key_from_str.exp.sub("_", name)


def get_s3_resource():
    try:
        access_key_id = os.environ[ENV_VAR_FOR_AWS_USER_ID]
        access_key = os.environ[ENV_VAR_FOR_AWS_USER_KEY]
        s3 = boto3.resource("s3", aws_access_key_id=access_key_id, aws_secret_access_key=access_key)
    except KeyError:
        log.error(f'Environment variable {ENV_VAR_FOR_AWS_USER_ID} or {ENV_VAR_FOR_AWS_USER_KEY} not found. '
                  f'Can\'t connect to S3 without credential.')
        return None
    except boto3_exceptions as err:
        log.error(f'Failed to connect to s3 because:\n{err}')
        return None
    return s3


def object_exist_in_bucket(s3, bucket, key):
    """check if key already exists in bucket. Return True if exists, False otherwise."""
    try:
        s3.Object(bucket, key).load()
    except boto3_exceptions.ClientError as e:
        return int(e.response['Error']['Code']) != 404
    return True


def _worker(q, s3_bucket_name, prefix, overwrite, picture_dir, lock, up_success, up_failed):
    with lock:
        s3 = get_s3_resource()
        if s3 is None:
            log.error(f"Thread {threading.get_ident()} failed to connect.")
            return -1
    success = []
    fail = []
    while True:
        try:
            pic_id, label = q.get(block=True, timeout=0.05)
        except queue.Empty:
            break
        picture = Path(picture_dir) / label["file_name"]
        key = prefix + pic_id
        if not overwrite and object_exist_in_bucket(s3, s3_bucket_name, key):
            log.warning(f'  --> Can\'t upload file "{picture}" because key "{key}" already exists in bucket "{s3_bucket_name}"')
            fail.append(pic_id)
        else:
            s3.meta.client.upload_file(str(picture), s3_bucket_name, key)
            success.append(pic_id)
    with lock:
        up_failed += fail
        up_success += success


def _print_progress(q, total):
    start_time = time.time()
    while not q.empty():
        finished = total - q.qsize()
        elapsed_time = time.time() - start_time
        progress_bar = tqdm.format_meter(finished, total, elapsed_time, ncols=100)
        print(f'{progress_bar}', end='')
        time.sleep(0.5)
        print('', end='\r', flush=True)
    finished = total - q.qsize()
    elapsed_time = time.time() - start_time
    progress_bar = tqdm.format_meter(finished, total, elapsed_time, ncols=100)
    print(f'{progress_bar}')


def upload_to_s3_from_label(d_label, picture_dir, s3_bucket_name, prefix="", overwrite=False, nb_of_thread=10):
    """
    Upload picture to s3 bucket.
    Note that credential to access the s3 bucket is retrieved from env variable (see variable name in the code)
    :param d_label:             [dict]      Dictionary of labels. Each label shall contains the following keys:
                                            "file_name": the name of the picture file
                                            "img_id": id that will be used to index the picture (shall be unique)
    :param picture_dir:         [string]    Path to the folder containing the pictures
    :param s3_bucket_name:      [string]    Name of the bucket
    :param prefix:              [string]    Prefix for every picture
    :param overwrite:           [bool]      If True, existing pic will be overwritten by new one sharing the same img_id
    :param nb_of_thread:        [int]       Number of thread
    :return:                    [tuple]     list of picture id successfully upladed, list of picture id failed to upload
    """
    already_exist_pic = []
    upload_success = []
    q = queue.Queue()
    for pic_id, label in d_label.items():
        item = (pic_id, label)
        q.put(item)
    l_thread = []
    lock = threading.RLock()
    for i in range(nb_of_thread):
        thread = threading.Thread(target=_worker, args=(q, s3_bucket_name, prefix, overwrite, picture_dir, lock,
                                                        upload_success, already_exist_pic))
        thread.start()
        l_thread.append(thread)
    _print_progress(q, len(d_label))
    for thread in l_thread:
        thread.join()
    return upload_success, already_exist_pic


def get_s3_formatted_bucket_path(bucket_name, key_prefix, file_name=None):
    """
    Creates a cleaned and well formatted name and path for access to s3 bucket from the bucket name and key prefix.
    If file_name is None, the function will return a key ended by a '/' (as for a key prefix)
    :param bucket_name:     [string]        s3 Bucket name
    :param key_prefix:      [string]        key prefix (s3 sub-folder)
    :param file_name:       [string]        OPTIONAL: name of the file. If defined, the function will return a
                                            path to file (not "/" terminated) and not to a bucket ("/" terminated)
    :return:                [tuple of str]  clean_full_path, clean_buck_name, clean_key

    For example:
    >>> get_s3_formatted_bucket_path("my-bucket/", "/sub/bucket//directory/with/typo")
    ("my-bucket/sub/bucket/directory/with/typo/", "my-bucket", "sub/bucket/directory/with/typo/")

    >>> get_s3_formatted_bucket_path("my-bucket/", "")
    ("my-bucket/", "my-bucket", "")

    >>> get_s3_formatted_bucket_path("my-bucket", "key_prefix/", "file.jpg")
    ("my-bucket/key_prefix/file.jpg", "my-bucket", "key_prefix/file.jpg")

    >>> get_s3_formatted_bucket_path("my-bucket", "", "key_prefix/file.jpg")
    ("my-bucket/key_prefix/file.jpg", "my-bucket", "key_prefix/file.jpg")

    >>> get_s3_formatted_bucket_path("my-bucket/key/prefix", "")
    ("my-bucket/key/prefix/", "my-bucket", "key/prefix/")

    >>> get_s3_formatted_bucket_path("my-bucket/key/prefix", "", "/file")
    ("my-bucket/key/prefix/file", "my-bucket", "key/prefix/file")
    """
    if file_name is None:
        raw_dir = bucket_name + "/" + key_prefix
    else:
        raw_dir = bucket_name + "/" + key_prefix + "/" + file_name
    dir_list_clean = [elm for elm in raw_dir.split("/") if bool(elm)]
    clean_full_path = "/".join(dir_list_clean)
    clean_key = "/".join(dir_list_clean[1:]) if len(dir_list_clean) > 1 else ""
    if file_name is None:
        clean_full_path += "/"
        clean_key += "/" if clean_key != "" else ""
    clean_bucket_name = dir_list_clean[0]
    return clean_full_path, clean_bucket_name, clean_key


def split_s3_path(bucket_key):
    l_bucket_key = [elm for elm in bucket_key.split("/") if bool(elm)]
    bucket = l_bucket_key[0]
    file_name = l_bucket_key[-1] if len(l_bucket_key) > 1 else ""
    key_prefix = "/".join(l_bucket_key[1:-1])
    key_prefix += "/" if bool(key_prefix) else ""
    return bucket, key_prefix, file_name


def delete_object_s3(bucket, l_object_key, s3_resource=None):
    """Delete all object in bucket with key listed in l_object_key"""
    if s3_resource is None:
        s3_resource = get_s3_resource()
    _, bucket, _ = get_s3_formatted_bucket_path(bucket, "")
    s3_bucket = s3_resource.Bucket(bucket)
    delete = {
        "Objects": []
    }
    for key in l_object_key:
        _, _, key = get_s3_formatted_bucket_path(bucket, "", key)
        delete["Objects"].append({"Key": key})
    return s3_bucket.delete_objects(Delete=delete)


def delete_all_in_s3_folder(bucket, key_prefix, s3_resource=None):
    if key_prefix == "" or key_prefix is None:
        log.info(f'Can\'t delete all the bucket, too dangerous... Please specify a key_prefix')
        return False
    if s3_resource is None:
        s3 = get_s3_resource()
    else:
        s3 = s3_resource
    bucket = s3.Bucket(bucket)
    for obj in bucket.objects.filter(Prefix=key_prefix):
        s3.Object(bucket.name, obj.key).delete()
    return True


def _download_worker(q, lock, output_dir, error_log):
    """
    Download file from an s3 bucket and write it to output_file
    :param q:               [queue obj] queue containing item to download as tuple (img_id, picture_label)
    :param lock:            [lock obj]  lock object
    :param output_dir:      [str]       Path to the directory where to download the pictures
    :param error_log:       [list]      List where errors will be appended
    """
    with lock:
        s3 = get_s3_resource()
        if s3 is None:
            log.error(f"Thread {threading.get_ident()} failed to connect.")
            return -1
    error = []
    while True:
        try:
            img_id, picture = q.get(block=True, timeout=0.05)
        except queue.Empty:
            break
        output_file = output_dir / picture["file_name"]
        bucket, key_prefix, file_name = split_s3_path(f'{picture["s3_bucket"]}/{img_id}')
        try:
            s3.meta.client.download_file(bucket, key_prefix + file_name, output_file.as_posix())
        except boto3_exceptions.ClientError as e:
            if e.response['Error']['Code'] != 404:
                log.error(f'Error: picture "{key_prefix + file_name}" not found in bucket {bucket}.')
                error.append((img_id, e.response['Error']['Code'], f'{e}'))
            else:
                log.error(f'Unexpected error: {e}')
                error.append((img_id, e.response['Error']['Code'], f'{e}'))
    with lock:
        error_log += error


def download_from_s3(d_picture, output_dir, nb_of_thread=10):
    """
    :param d_picture:       [dict]      Dictionary of downloaded pictures as follow:
                                        {
                                            img_id: {
                                                "img_id": id,
                                                "file_name": "pic_file_name.jpg",
                                                "s3_bucket": "s3_bucket_path"
                                            },
                                            ...
                                        }
    :param output_dir:      [str]       Path to the directory where to save the pictures
    """
    lock = threading.RLock()
    q = queue.Queue()
    error_log = []
    for img_id, picture in d_picture.items():
        q.put((img_id, picture))
    for i in range(nb_of_thread):
        thread = threading.Thread(target=_download_worker, args=(q, lock, output_dir, error_log))
        thread.start()
    _print_progress(q, len(d_picture))
    success = len(d_picture) - len(error_log)
    if len(error_log) > 0:
        log.info(f'{len(error_log)} pictures couldn\'t be download')
    log.info(f'{success} pictures have successfully been downloaded to "{output_dir}"')
