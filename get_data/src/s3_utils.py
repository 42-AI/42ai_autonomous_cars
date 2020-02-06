from pathlib import Path
import re
import os
import boto3
from botocore import exceptions as boto3_exceptions
from tqdm import tqdm

from conf.cluster_conf import ENV_VAR_FOR_AWS_USER_ID, ENV_VAR_FOR_AWS_USER_KEY


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
        print(f'Environment variable {ENV_VAR_FOR_AWS_USER_ID} or {ENV_VAR_FOR_AWS_USER_KEY} not found. '
              f'Can\'t connect to S3 without credential.')
        return None
    except boto3_exceptions as err:
        print(f'Failed to connect to s3 because:\n{err}')
        return None
    return s3


def file_exist_in_bucket(s3, bucket, key):
    """check if key already exists in bucket. Return True if exists, False otherwise."""
    try:
        s3.Object(bucket, key).load()
    except boto3_exceptions.ClientError as e:
        return int(e.response['Error']['Code']) != 404
    return True


def upload_to_s3_from_label(d_label, s3_bucket_name, prefix="", overwrite=False):
    """
    Upload picture to s3 bucket.
    Note that credential to access the s3 bucket is retrieved from env variable (see variable name in the code)
    :param d_label:             [dict]      Dictionary of labels. Each label shall contains the following keys:
                                            "file_name": the name of the picture file
                                            "location": path to the picture directory
                                            "img_id": id that will be used to index the picture (shall be unique)
    :param s3_bucket_name:      [string]    Name of the bucket
    :param prefix:              [string]    Prefix for every picture
    :param overwrite:           [bool]      If True, existing pic will be overwritten by new one sharing the same img_id
    :return:                    [tuple]     list of picture id successfully upladed, list of picture id failed to upload
    """
    s3 = get_s3_resource()
    if s3 is None:
        exit(1)
    already_exist_pic = []
    upload_success = []
    log = ""
    for pic_id, label in tqdm(d_label.items()):
        picture = Path(label["location"]) / label["file_name"]
        key = prefix + pic_id
        if not overwrite and file_exist_in_bucket(s3, s3_bucket_name, key):
            log += f'  --> Can\'t upload file "{picture}" because key "{key}" already exists in bucket "{s3_bucket_name}"\n'
            already_exist_pic.append(pic_id)
        else:
            s3.meta.client.upload_file(str(picture), s3_bucket_name, key)
            upload_success.append(pic_id)
    print(log)
    return upload_success, already_exist_pic


def get_s3_formatted_bucket_path(bucket_name, key_prefix, file_name=None):
    """
    Creates a cleaned and well formatted name and path for access to s3 bucket from the bucket name and key prefix.
    If file_name is given, the function will return a file path instead of a key_prefix path.
    :param bucket_name:     [string]        s3 Bucket name
    :param key_prefix:      [string]        key prefix (s3 sub-folder)
    :param file_name:       [string]        OPTIONAL: name of the file. If defined, the function will return a
                                            path to file (not "/" terminated) and not to a bucket ("/" terminated)
    :return:                [tuple of str]  clean_full_path, clean_buck_name, clean_key_prefix

    For example:
    >>> get_s3_formatted_bucket_path("my-bucket/", "/sub/bucket//directory/with/typo")
    ("my-bucket/sub/bucket/directory/with/typo/", "my-bucket", "sub/bucket/directory/with/typo/")

    >>> get_s3_formatted_bucket_path("my-bucket/", "")
    ("my-bucket/", "my-bucket", "")

    >>> get_s3_formatted_bucket_path("my-bucket", "key_prefix/", "file.jpg")
    ("my-bucket/key_prefix/file.jpg", "my-bucket", "key_prefix/file.jpg")

    >>> get_s3_formatted_bucket_path("my-bucket", "", "key_prefix/file.jpg")
    ("my-bucket/key_prefix/file.jpg", "my-bucket", "key_prefix/file.jpg")
    """
    if file_name is None:
        raw_dir = bucket_name + "/" + key_prefix
    else:
        raw_dir = bucket_name + "/" + key_prefix + "/" + file_name
    dir_list_clean = [elm for elm in raw_dir.split("/") if bool(elm)]
    clean_full_path = "/".join(dir_list_clean)
    clean_key_prefix = "/".join(dir_list_clean[1:]) if len(dir_list_clean) > 1 else ""
    if file_name is None:
        clean_full_path += "/"
        clean_key_prefix += "/" if clean_key_prefix != "" else ""
    clean_bucket_name = dir_list_clean[0]
    return clean_full_path, clean_bucket_name, clean_key_prefix


def split_s3_path(bucket_key):
    l_bucket_key = [elm for elm in bucket_key.split("/") if bool(elm)]
    bucket = l_bucket_key[0]
    file_name = l_bucket_key[-1] if len(l_bucket_key) > 1 else ""
    key_prefix = "/".join(l_bucket_key[1:-1])
    key_prefix += "/" if bool(key_prefix) else ""
    return bucket, key_prefix, file_name


def delete_object_s3(bucket, key_prefix, l_object_key, s3_resource=None):
    """Delete all object listed in l_object_key and with prefix key_prefix"""
    full_path, bucket, key_prefix = get_s3_formatted_bucket_path(bucket, key_prefix)
    if s3_resource is None:
        s3_resource = get_s3_resource()
    s3_bucket = s3_resource.Bucket(bucket)
    delete = {
        "Objects": []
    }
    for key in l_object_key:
        delete["Objects"].append({"Key": key_prefix + key})
    return s3_bucket.delete_objects(Delete=delete)


def delete_all_in_s3_folder(bucket, key_prefix, s3_resource=None):
    if key_prefix == "" or key_prefix is None:
        print(f'Can\'t delete all the bucket, to dangerous... Please specify a key_prefix')
        return False
    if s3_resource is None:
        s3 = get_s3_resource()
    else:
        s3 = s3_resource
    bucket = s3.Bucket(bucket)
    for obj in bucket.objects.filter(Prefix=key_prefix):
        s3.Object(bucket.name, obj.key).delete()
    return True


def download_from_s3(picture_id, bucket_key, output_file):
    """
    Download file from an s3 bucket and write it to output_file
    :param picture_id:      [string]    Id of the picture (as stored in s3)
    :param bucket_key:      [string]    bucket and key concatenated (eg: "my-bucket/key_prefix/img_id")
    :param output_file:     [string]    Path to the output_file
    :return:                [object]    Return None if download went OK
    """
    s3 = get_s3_resource()
    if s3 is None:
        exit(1)
    bucket, key_prefix, file_name = split_s3_path(f'{bucket_key}/{picture_id}')
    return s3.meta.client.download_file(bucket, key_prefix + file_name, output_file)
