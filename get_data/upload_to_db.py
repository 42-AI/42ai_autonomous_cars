from pathlib import Path
import json
import boto3
from botocore.exceptions import ClientError
import os


def is_single_label(label):
    if not isinstance(label, list):
        return True
    return False


def file_exist_in_bucket(s3, bucket, key):
    try:
        s3.Object(bucket, key).load()
    except ClientError as e:
        return int(e.response['Error']['Code']) != 404
    return True


def upload_label_to_s3(l_label, s3_bucket, prefix=""):
    access_key_id = os.environ["PATATE_S3_KEY_ID"]
    access_key = os.environ["PATATE_S3_KEY"]
    already_exist_pic = []
    upload_success = []
    s3 = boto3.resource("s3", aws_access_key_id=access_key_id, aws_secret_access_key=access_key)
    for label in l_label:
        picture = Path(label["location"]) / label["file_name"]
        pic_id = label["img_id"]
        key = prefix + pic_id
        if file_exist_in_bucket(s3, s3_bucket, key):
            print(f'Can\'t upload file "{picture}" because key "{key}" already exists in bucket "{s3_bucket}"')
            already_exist_pic.append(pic_id)
        else:
            s3.meta.client.upload_file(str(picture), s3_bucket, key)
            print(f'Picture "{picture} successfully uploaded to {s3_bucket} with key "{key}"')
            upload_success.append(pic_id)
    return upload_success, already_exist_pic


def filter_out_missing_pic(label_list):
    missing_pic_id = []
    for i, label in enumerate(label_list):
        pics = Path(label["location"]) / label["file_name"]
        if not pics.is_file():
            print(f'Picture "{pics}" can''t be found.')
            missing_pic_id.append(label["img_id"])
    valid_label = [label for label in label_list if label["img_id"] not in missing_pic_id]
    return valid_label, missing_pic_id


def edit_label(l_label, field, value):
    """Set one field of a list of label to a value."""
    for label in l_label:
        label[field] = value


def print_synthesis(bucket, prefix, missing_pic, already_exist_pic, upload_success):
    print('----------------------------------------')
    print('Upload Completed !')
    print(f'Upload bucket: "{bucket + "/" + prefix}"')
    print(f'Number of picture uploaded: {len(upload_success)}')
    print(f'Number of failed upload: {len(missing_pic) + len(already_exist_pic)}')
    if len(missing_pic) > 0:
        print(f'  --> Picture not found:                   {missing_pic}')
    if len(already_exist_pic) > 0:
        print(f'  --> Picture id already exists in bucket: {already_exist_pic}')


def upload_to_db(label_file, s3_bucket, key_prefix):
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
    :param label_file:
    :param s3_bucket:
    :param key_prefix:
    :return:
    """
    if not Path(label_file).is_file():
        print(f'File "{label_file}" can''t be found.')
        exit(0)
    with Path(label_file).open(mode='r', encoding='utf-8') as fp:
        l_label = json.load(fp)
    if is_single_label(l_label):
        l_label = [l_label]
    l_label, missing_pic = filter_out_missing_pic(l_label)
    upload_success, already_exist_pic = upload_label_to_s3(l_label, s3_bucket, key_prefix)
    print_synthesis(s3_bucket, key_prefix, missing_pic, already_exist_pic, upload_success)
    l_label = [label for label in l_label if label["img_id"] in upload_success]
    edit_label(l_label, "location", s3_bucket)
    print(f'list label success = {l_label}')
    return l_label


if __name__ == "__main__":
    label_file = "sample/labels.json"
    # label_file = "sample/single_label.json"
    s3_bucket = "032854191254-patate"
    key_prefix = "test/"
    l_label = upload_to_db(label_file, s3_bucket, key_prefix)
    exit(0)
    edit_label(l_label, "location", "/Users/jjauzion/42/42ai_autonomous_cars/get_data/sample")
