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


def upload_label_to_s3(l_label, s3_bucket):
    access_key_id = os.environ["PATATE_S3_KEY_ID"]
    access_key = os.environ["PATATE_S3_KEY"]
    s3 = boto3.resource("s3", aws_access_key_id=access_key_id, aws_secret_access_key=access_key)
    for label in l_label:
        pics = Path(label["location"]) / label["file_name"]
        key = label["img_id"]
        if file_exist_in_bucket(s3, s3_bucket, key):
            print(f'Can\'t upload file "{pics}" because key "{key}" already exists in bucket "{s3_bucket}"')
            return False
        s3.meta.client.upload_file(str(pics), s3_bucket, key)
        print(f'Picture "{pics} successfully uploaded to {s3_bucket} with key "{key}"')
    return True


def filter_out_missing_pic(label_list):
    missing_pic = []
    for i, label in enumerate(label_list):
        pics = Path(label["location"]) / label["file_name"]
        if not pics.is_file():
            print(f'Picture "{pics}" can''t be found.')
            missing_pic.append(i)
    return [label for i, label in enumerate(label_list) if i not in missing_pic]


def upload_to_db(label_file, s3_bucket):
    """
    Upload picture(s) to the DataBase according to the label file.
    Labels are uploaded to ES cluster, picture to S3 bucket
    :param label_file:
    :param s3_bucket:
    :return:
    """
    if not Path(label_file).is_file():
        print(f'File "{label_file}" can''t be found.')
        exit(0)
    with Path(label_file).open(mode='r', encoding='utf-8') as fp:
        l_label = json.load(fp)
    if is_single_label(l_label):
        l_label = [l_label]
    l_label = filter_out_missing_pic(l_label)
    upload_label_to_s3(l_label, s3_bucket)
    return l_label


if __name__ == "__main__":
    label_file = "sample/labels.json"
    label_file = "sample/single_label.json"
    s3_bucket = "032854191254-patate"
    l_label = upload_to_db(label_file, s3_bucket)
