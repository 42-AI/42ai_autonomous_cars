from pathlib import Path
import json
import boto3
import os


def is_single_label(label):
    if not isinstance(label, list):
        return True
    return False


def upload_to_s3(file, key):
    access_key_id = os.environ[""]


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
    missing_pic = 0
    for label in l_label:
        pics = Path(label["location"]) / label["file_name"]
        if not pics.is_file():
            print(f'Picture "{pics}" can''t be found.')
            missing_pic += 1
        else:
            print(label)
    return l_label


if __name__ == "__main__":
    label = "sample/labels.json"
    label = "sample/single_label.json"
    l_label = upload_to_db(label)
    print(l_label)
