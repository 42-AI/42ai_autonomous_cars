from pathlib import Path
import json

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


def upload_synthesis(upload_bucket_path, missing_pic, already_exist_pic, s3_success, failed_es):
    success = len(s3_success) - len(failed_es)
    fail = len(missing_pic) + len(already_exist_pic) + len(failed_es)
    print('----------------------------------------')
    print('Upload Completed !')
    print(f'{success} picture(s) were successful uploaded.')
    print(f'{fail} upload failed.')
    print(f'Upload bucket: "{upload_bucket_path}"')
    print(f'Number of picture uploaded to s3 bucket : {len(s3_success)}')
    print(f'Number of failed upload to s3 bucket: {len(missing_pic) + len(already_exist_pic)}')
    if len(missing_pic) > 0:
        print(f'  --> Picture not found:                   {missing_pic}')
    if len(already_exist_pic) > 0:
        print(f'  --> Picture id already exists in bucket: {already_exist_pic}')
    print(f'Number of failed upload to ES cluster: {len(failed_es)}')
    if len(failed_es) > 0:
        print(f'  --> List of failed pic id: {already_exist_pic}')
    return success, fail


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


def upload_to_db(label_file, bucket_name, key_prefix, es_host_ip, es_port, es_index, overwrite=False):
    """
    Upload picture(s) to the DataBase according to the label file.
    Labels are uploaded to Elasticsearch cluster ; pictures are uploaded to S3 bucket.
    Label file shall be in json format. It can contain one document or a list of document. Each document shall at least
    have the following fields:
    [
      {
        "img_id": "xxx",
        "file_name": "file-name.jpg",
        "location": "/path/to/picture/dir/"
      }
    ]
    then you can add any field you wish to labelized the picture.
    :param label_file:          [string]    path to the file containing the labels in json format
    :param bucket_name:         [string]    Name of the s3 bucket
    :param key_prefix:          [string]    Prefix for every uploaded picture to s3. Unix path system (use slashes: '/')
                                            For example if:
                                            bucket_name = "my-bucket", key_prefix = "subfolder/"
                                            Every picture will be uploaded to "my-bucket/subfolder/{img-id}"
    :param es_host_ip:          [string]    Public ip of the Elasticsearch host server
    :param es_port:             [int]       Port open for Elasticsearch on host server (typically 9200)
    :param es_index:            [string]    Name of the index to use
    :param overwrite:           [bool]      If True will overwrite picture is s3 and label in ES if same img_id is found
                                            If False (default), only non existing img_id picture will be uploaded
    :return:                    [tuple]     (int) Number of successful upload, (int) number of failed upload
                                            Return None on error
    """
    l_label = get_label_list_from_file(label_file)
    if l_label is None:
        return None, None
    print(f'Looking for pictures...')
    l_label, missing_pic = filter_out_missing_pic(l_label)
    print(f'Uploading to s3...')
    upload_bucket_dir, bucket_name, key_prefix = s3_utils.get_s3_formatted_bucket_path(bucket_name, key_prefix)
    s3_upload_success, already_exist_pic = s3_utils.upload_to_s3_from_label(l_label, bucket_name, key_prefix, overwrite)
    l_label = [label for label in l_label if label["img_id"] in s3_upload_success]
    edit_label(l_label, "location", upload_bucket_dir)
    print(f'Uploading to Elasticsearch cluster...')
    failed_es_upload = es_utils.upload_to_es(
        l_label=l_label, index=es_index, host_ip=es_host_ip, port=es_port, update=overwrite)
    success, fail = upload_synthesis(upload_bucket_dir, missing_pic, already_exist_pic, s3_upload_success, failed_es_upload)
    return success, fail
