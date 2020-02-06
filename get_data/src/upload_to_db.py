from pathlib import Path
import json
from datetime import datetime

from get_data.src import s3_utils
from get_data.src import es_utils
from get_data.src import utils_fct


def remove_missing_pic_from_dic(label_dict):
    """
    Check if all pictures referenced in the label_dict exists. All non existing picture are removed from label_dict
    (modification in-place).
    :param label_dict:      [dict]  dictionary of label with the following format (at least those 3 keys are required):
                                    {
                                        img_id: {
                                            "img_id": id,
                                            "file_name": "pic_file_name.jpg",
                                            "location": "s3_bucket_path"
                                        },
                                        ...
                                    }
    :return:                [list] list of missing pictures id
    """
    missing_pic_id = []
    for img_id, label in label_dict.items():
        pics = Path(label["location"]) / label["file_name"]
        if not pics.is_file():
            print(f'  --> Picture "{pics}" can\'t be found.')
            missing_pic_id.append(label["img_id"])
    for key in missing_pic_id:
        label_dict.pop(key)
    return missing_pic_id


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


def _get_label_event_and_date(d_label):
    """Read a dictionary of label and return the event name and date of the first label found in the dict"""
    try:
        first_key = next(iter(d_label))
        event = d_label[first_key]["event"]
        date = datetime.strptime(d_label[first_key]["timestamp"], "%Y%m%dT%H-%M-%S-%f")
    except KeyError:
        return None, None
    except ValueError as err:
        print(f'Error: could not parse date because : {err}')
        return None, None
    return event, date


def generate_key_prefix(d_label):
    """
    Generate the key key_prefix for a list of label.
    Return None if one of the following test fail:
        Check that the "event" name is well formated for s3 bucket key.
        Check all label in the list have the same "event" name
    Return the key_prefix if tests are OK. Key key_prefix is defined as follow:
        "{event_name}/{picture_date}/"
        Note: the date will be the date of the first picture in the label list
    :param d_label:     [dict]  Dict of labels
    :return:            [str]   key key_prefix: "{event_name}/{picture_date}/"
    """
    event, date = _get_label_event_and_date(d_label)
    if event is None or date is None:
        return None
    for key, label in d_label.items():
        is_valid, regex = s3_utils.is_valid_s3_key(label["event"])
        if not is_valid:
            print(f'Event name "{label["event"]} contains invalid characters. Char is invalid if it match with:{regex}')
            return None
        if label["event"] != event:
            print(f'Key bucket can\'t be generated because event name is not unique. Got {event} and {label["event"]}.')
            return None
    return f'{event}/{date.strftime("%Y%m%d")}/'


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
        "label_fingerprint": "c072a1b9a16b633d6b3004c3edab7553",
        "event": "event_name"
      }
    ]
    then you can add any field you wish to labelized the picture.
    Note: if the picture already exists in s3 and is not overwritten, upload to ES will be tried anyway.
    :param label_file:      [string]    path to the file containing the labels in json format
    :param bucket_name:     [string]    Name of the s3 bucket
    :param es_host_ip:      [string]    Public ip of the Elasticsearch host server
    :param es_port:         [int]       Port open for Elasticsearch on host server (typically 9200)
    :param es_index:        [string]    Name of the index to use
    :param overwrite:       [bool]      If True, new picture will overwrite existing ones in S3 with same img_id and new
                                        label will overwrite existing one in ES with same label_fingerprint
                                        If False (default), only non existing picture and label will be uploaded
    :param key_prefix:      [string]    If None, default key is used. Default key is as follow:
                                        {event_name}/{upload_date}/
                                        So the picture will be uploaded to:
                                        "https://s3.amazonaws.com/{my-bucket}/{event_name}/{picture_date}/"
    :return:                [tuple]     (int) s3 success upload, (int) ES success upload, (int) total nb of failed upload
    """
    d_label = utils_fct.get_label_dict_from_file(label_file)
    total_label = len(label_file)
    if d_label is None:
        return 0, 0, total_label
    print(f'Looking for pictures...')
    missing_pic = remove_missing_pic_from_dic(d_label)
    if len(d_label) == 0:
        return 0, 0, total_label
    if key_prefix is None:
        key_prefix = generate_key_prefix(d_label)
        if key_prefix is None:
            return 0, 0, total_label
    upload_bucket_dir, bucket_name, key_prefix = s3_utils.get_s3_formatted_bucket_path(bucket_name, key_prefix)
    print(f'Uploading to s3...')
    s3_upload_success, already_exist_pic = s3_utils.upload_to_s3_from_label(d_label, bucket_name, key_prefix, overwrite)
    utils_fct.edit_label(d_label, "location", upload_bucket_dir)
    utils_fct.edit_label(d_label, "upload_date", datetime.now().strftime("%Y%m%dT%H-%M-%S-%f"))
    print(f'Uploading to Elasticsearch cluster...')
    failed_es_upload = es_utils.upload_to_es(
        d_label=d_label, index=es_index, host_ip=es_host_ip, port=es_port, overwrite=overwrite)
    es_success = len(d_label) - len(failed_es_upload)
    print_upload_synthesis(upload_bucket_dir, es_index,
                           es_success, failed_es_upload, len(s3_upload_success), missing_pic, already_exist_pic)
    return len(s3_upload_success), es_success, len(failed_es_upload) + len(already_exist_pic) + len(missing_pic)
