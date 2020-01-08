from pathlib import Path
import json
import os
import boto3
from botocore.exceptions import ClientError
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch.helpers.errors import BulkIndexError

from get_data import cluster_param


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


def upload_label_to_s3(l_label, s3_bucket_name, prefix=""):
    access_key_id = os.environ["PATATE_S3_KEY_ID"]
    access_key = os.environ["PATATE_S3_KEY"]
    already_exist_pic = []
    upload_success = []
    s3 = boto3.resource("s3", aws_access_key_id=access_key_id, aws_secret_access_key=access_key)
    for label in l_label:
        picture = Path(label["location"]) / label["file_name"]
        pic_id = label["img_id"]
        key = prefix + pic_id
        if file_exist_in_bucket(s3, s3_bucket_name, key):
            print(f'  --> Can\'t upload file "{picture}" because key "{key}" already exists in bucket "{s3_bucket_name}"')
            already_exist_pic.append(pic_id)
        else:
            s3.meta.client.upload_file(str(picture), s3_bucket_name, key)
            upload_success.append(pic_id)
    return upload_success, already_exist_pic


def gen_bulk_doc(l_label, index):
    for label in l_label:
        yield {
            "_index": index,
            "_type": "document",
            "_op_type": "create",
            "_id": label["img_id"],
            "_source": label
        }


def upload_to_es(l_label, index, host_ip, port):
    try:
        user = os.environ["ES_USER_ID"]
        pwd = os.environ["ES_USER_PWD"]
    except KeyError as err:
        print("  --> Warning: Elasticsearch 'user' and/or password not found. Trying connection without auth...")
        user = ""
        pwd = ""
    es = Elasticsearch([{"host": host_ip, "port": port}], http_auth=(user, pwd))
    failed_doc_id = []
    success, errors = helpers.bulk(es, gen_bulk_doc(l_label, index=index), request_timeout=60, raise_on_error=False)
    for error in errors:
        for error_type in error:
            failed_doc_id.append(error[error_type]["_id"])
            print(f'  --> Couldn\'t upload document "{failed_doc_id[-1]} because : {error[error_type]["error"]["reason"]}')
    return failed_doc_id


def filter_out_missing_pic(label_list):
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


def print_synthesis(upload_bucket_path, missing_pic, already_exist_pic, s3_success, failed_es):
    print('----------------------------------------')
    print('Upload Completed !')
    print(f'{len(s3_success) - len(failed_es)} picture(s) were successful uploaded.')
    print(f'{len(missing_pic) + len(already_exist_pic) + len(failed_es)} upload failed.')
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


def get_s3_formatted_bucket_path(bucket_name, prefix):
    """
    Assemble a clean s3 bucket directory from bucket name and key prefix and return well formated name and
    path for s3 upload.
    For example:
    bucket_name = "my-bucket/"
    prefix = "/sub/bucket//directory/with/typo
    will output:
    clean_full_path = "my-bucket/sub/bucket/directory/with/typo/"
    clean_bucket_name = "my-bucket"
    clean_key_prefix = "sub/bucket/directory/with/typo/"
    :param bucket_name:     [string]    s3 Bucket name
    :param prefix:          [string]    key prefix (s3 sub-folder)
    :return: clean_full_path, clean_buck_name, clean_key_prefix
    """
    raw_dir = bucket_name + "/" + prefix
    dir_list_clean = [elm for elm in raw_dir.split("/") if bool(elm)]
    clean_full_path = "/".join(dir_list_clean) + "/"
    clean_key_prefix = "/".join(dir_list_clean[1:]) + "/" if len(dir_list_clean) > 1 else ""
    clean_bucket_name = dir_list_clean[0]
    return clean_full_path, clean_bucket_name, clean_key_prefix


def upload_to_db(label_file, bucket_name, key_prefix, es_host_ip, es_port, es_index):
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
    :param bucket_name:
    :param key_prefix:
    :param es_cluster_param:
    :return:
    """
    if not Path(label_file).is_file():
        print(f'File "{label_file}" can''t be found.')
        exit(0)
    with Path(label_file).open(mode='r', encoding='utf-8') as fp:
        l_label = json.load(fp)
    if is_single_label(l_label):
        l_label = [l_label]
    print(f'Looking for pictures...')
    l_label, missing_pic = filter_out_missing_pic(l_label)
    print(f'Uploading to s3...')
    upload_bucket_dir, bucket_name, key_prefix = get_s3_formatted_bucket_path(bucket_name, key_prefix)
    s3_upload_success, already_exist_pic = upload_label_to_s3(l_label, bucket_name, key_prefix)
    l_label = [label for label in l_label if label["img_id"] in s3_upload_success]
    edit_label(l_label, "location", upload_bucket_dir)
    print(f'Uploading to Elasticsearch cluster...')
    failed_es_upload = upload_to_es(l_label=l_label, index=es_index, host_ip=es_host_ip, port=es_port)
    print_synthesis(upload_bucket_dir, missing_pic, already_exist_pic, s3_upload_success, failed_es_upload)
    return l_label


if __name__ == "__main__":
    label_file = "sample/labels.json"
    # label_file = "sample/single_label.json"
    s3_bucket = "032854191254-patate"
    key_prefix = ""
    es_ip_host = cluster_param.ES_HOST_IP
    es_port_host = cluster_param.ES_HOST_PORT
    es_index_name = cluster_param.ES_INDEX
    l_label = upload_to_db(label_file, s3_bucket, key_prefix, es_ip_host, es_port_host, es_index_name)
    exit(0)
    edit_label(l_label, "location", "/Users/jjauzion/42/42ai_autonomous_cars/get_data/sample")
