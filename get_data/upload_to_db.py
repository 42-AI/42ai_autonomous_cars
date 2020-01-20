from pathlib import Path
import json
from datetime import datetime

from .utils import s3_utils
from .utils import es_utils


def is_single_label(label):
    """Return True if label contains a single label {...} ; False if it contains a list of label [{...}, {...}, ...]."""
    if isinstance(label, list):
        return False
    return True


def filter_out_missing_pic(label_list):
    """
    Check if all pictures referenced in the label_list exists.
    Return a list of valid_label (picture exists) and a list of missing picture id
    :param label_list:      [list]  list of label
    :return:                [tuple] list of valid label (picture exists) and list of missing pictures id
    """
    missing_pic_id = []
    for i, label in enumerate(label_list):
        pics = Path(label["location"]) / label["file_name"]
        if not pics.is_file():
            print(f'  --> Picture "{pics}" can\'t be found.')
            missing_pic_id.append(label["img_id"])
    valid_label = [label for label in label_list if label["img_id"] not in missing_pic_id]
    return valid_label, missing_pic_id


def edit_label(l_label, field, value):
    """Set one field of a list of label to a value."""
    for label in l_label:
        label[field] = value


def print_upload_synthesis(bucket, index_name, es_success, failed_es, s3_success, missing_pic, already_exist_pic):
    print('----------------------------------------')
    print(f'Upload Completed ! {s3_success} picture(s) uploaded to s3 and {es_success} uploaded to ES')
    print(f'Upload to s3:')
    print(f' Upload bucket: "{bucket}"')
    print(f' {s3_success} picture(s) were successful uploaded to s3.')
    print(f' {len(missing_pic) + len(already_exist_pic)} upload failed to s3.')
    if len(missing_pic) > 0:
        print(f'   --> Picture not found:                   {missing_pic}')
    if len(already_exist_pic) > 0:
        print(f'   --> Picture id already exists in bucket: {already_exist_pic}')
    print(f'Upload ES:')
    print(f' Index name: "{index_name}"')
    print(f' {es_success} picture(s) were successful uploaded to ES.')
    print(f' {len(failed_es)} upload failed to ES.')
    if len(failed_es) > 0:
        print(f'   --> List of failed pic id: {failed_es}')


def get_label_list_from_file(file):
    """Open and read file containing the label(s). Return a list of label or None on errors."""
    if not Path(file).is_file():
        print(f'File "{file}" can\'t be found.')
        return None
    with Path(file).open(mode='r', encoding='utf-8') as fp:
        l_label = json.load(fp)
    if is_single_label(l_label):
        l_label = [l_label]
    return l_label


def generate_key_prefix(l_label):
    """
    Generate the key prefix for a list of label.
    Return None if one ofthe following test fail:
        Check that the "event" name is well formated for s3 bucket key.
        Check all label in the list have the same "event" name
    Return the key_prefix if test are OK. Key prefix is defined as follow:
        "{event_name}/{today_date}/"
    :param l_label:     [list]  list of labels
    :return:            [str]   key prefix: "{event_name}/{today_date}/"
    """
    try:
        event = l_label[0]["event"]
    except KeyError:
        return None
    for label in l_label:
        is_valid, regex = s3_utils.is_valid_s3_key(label["event"])
        if not is_valid:
            print(f'Event name "{label["event"]} contains invalid characters. Char is invalid if it match with:{regex}')
            return None
        if label["event"] != event:
            print(f'Key bucket can\'t be generated because event name is not unique. Got {event} and {label["event"]}.')
            return None
    date = datetime.now().strftime("%Y%m%d")
    return f'{event}/{date}/'


def upload_to_db(label_file, bucket_name, es_host_ip, es_port, es_index, key_prefix=None, overwrite=False):
    """
    Upload picture(s) to the DataBase according to the label file.
    Labels are uploaded to Elasticsearch cluster ; pictures are uploaded to S3 bucket.
    Label file shall be in json format. It can contain one document or a list of document. Each document shall at least
    have the following fields:
    [
      {
        "img_id": "xxx",
        "file_name": "file-name.jpg",
        "location": "/path/to/picture/dir/",
        "event": "event_name"
      }
    ]
    then you can add any field you wish to labelized the picture.
    Note: if picture already exist in s3 and is not overwritten, upload to ES will be tried anyway.
    :param label_file:      [string]    path to the file containing the labels in json format
    :param bucket_name:     [string]    Name of the s3 bucket
    :param es_host_ip:      [string]    Public ip of the Elasticsearch host server
    :param es_port:         [int]       Port open for Elasticsearch on host server (typically 9200)
    :param es_index:        [string]    Name of the index to use
    :param overwrite:       [bool]      If True will overwrite picture is s3 and label in ES if same img_id is found
                                        If False (default), only non existing img_id picture will be uploaded
    :param key_prefix:      [string]    If None, default key is used. Default key is as follow:
                                        {event_name}/{upload_date}/
                                        So the picture will be uploaded to:
                                        "https://s3.amazonaws.com/{my-bucket}/{event_name}/{upload_date}/"
    :return:                [tuple]     (int) s3 success upload, (int) ES success upload, (int) total nb of upload error
                                        Return None, None, None on error
    """
    l_label = get_label_list_from_file(label_file)
    if l_label is None:
        return None, None, None
    print(f'Looking for pictures...')
    l_label, missing_pic = filter_out_missing_pic(l_label)
    if len(l_label) == 0:
        return 0, 0, len(missing_pic)
    if key_prefix is None:
        key_prefix = generate_key_prefix(l_label)
        if key_prefix is None:
            return None, None, None
    upload_bucket_dir, bucket_name, key_prefix = s3_utils.get_s3_formatted_bucket_path(bucket_name, key_prefix)
    print(f'Uploading to s3...')
    s3_upload_success, already_exist_pic = s3_utils.upload_to_s3_from_label(l_label, bucket_name, key_prefix, overwrite)
    edit_label(l_label, "location", upload_bucket_dir)
    edit_label(l_label, "upload_date", datetime.now().strftime("%Y%m%dT%H-%M-%S-%f"))
    print(f'Uploading to Elasticsearch cluster...')
    failed_es_upload = es_utils.upload_to_es(
        l_label=l_label, index=es_index, host_ip=es_host_ip, port=es_port, update=overwrite)
    es_success = len(l_label) - len(failed_es_upload)
    print_upload_synthesis(upload_bucket_dir, es_index,
                           es_success, failed_es_upload, len(s3_upload_success), missing_pic, already_exist_pic)
    return len(s3_upload_success), es_success, len(failed_es_upload) + len(already_exist_pic) + len(missing_pic)
