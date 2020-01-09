from pathlib import Path
import os
import boto3
from botocore.exceptions import ClientError


def get_s3_resource():
    access_key_id = os.environ["PATATE_S3_KEY_ID"]
    access_key = os.environ["PATATE_S3_KEY"]
    return boto3.resource("s3", aws_access_key_id=access_key_id, aws_secret_access_key=access_key)


def file_exist_in_bucket(s3, bucket, key):
    """check if key already exists in bucket. Return True if exists, False otherwise."""
    try:
        s3.Object(bucket, key).load()
    except ClientError as e:
        return int(e.response['Error']['Code']) != 404
    return True


def upload_to_s3_from_label(l_label, s3_bucket_name, prefix="", overwrite=False):
    """
    Upload picture to s3 bucket.
    Note that credential to access the s3 bucket is retrieved from env variable (see variable name in the code)
    :param l_label:             [list]      List of labels. Each label shall contains the following keys:
                                            "file_name": the name of the picture file
                                            "location": path to the picture directory
                                            "img_id": id that will be used to index the picture (shall be unique)
    :param s3_bucket_name:      [string]    Name of the bucket
    :param prefix:              [string]    Prefix for every picture
    :param overwrite:           [bool]      If True, existing pic will be overwritten by new one sharing the same img_id
    :return:                    [tuple]     list of picture id successfully upladed, list of picture id failed to upload
    """
    s3 = get_s3_resource()
    already_exist_pic = []
    upload_success = []
    for label in l_label:
        picture = Path(label["location"]) / label["file_name"]
        pic_id = label["img_id"]
        key = prefix + pic_id
        if not overwrite and file_exist_in_bucket(s3, s3_bucket_name, key):
            print(f'  --> Can\'t upload file "{picture}" because key "{key}" already exists in bucket "{s3_bucket_name}"')
            already_exist_pic.append(pic_id)
        else:
            s3.meta.client.upload_file(str(picture), s3_bucket_name, key)
            upload_success.append(pic_id)
    return upload_success, already_exist_pic


def get_s3_formatted_bucket_path(bucket_name, prefix):
    """
    Creates a cleaned and well formatted name and path for upload to s3 bucket from the bucket name and key prefix.
    :param bucket_name:     [string]        s3 Bucket name
    :param prefix:          [string]        key prefix (s3 sub-folder)
    :return:                [tuple of str]  clean_full_path, clean_buck_name, clean_key_prefix

    For example:
    >>> get_s3_formatted_bucket_path("my-bucket/", "/sub/bucket//directory/with/typo")
    ("my-bucket/sub/bucket/directory/with/typo/", "my-bucket", "sub/bucket/directory/with/typo/")

    >>> get_s3_formatted_bucket_path("my-bucket/", "")
    ("my-bucket/", "my-bucket", "")
    """
    raw_dir = bucket_name + "/" + prefix
    dir_list_clean = [elm for elm in raw_dir.split("/") if bool(elm)]
    clean_full_path = "/".join(dir_list_clean) + "/"
    clean_key_prefix = "/".join(dir_list_clean[1:]) + "/" if len(dir_list_clean) > 1 else ""
    clean_bucket_name = dir_list_clean[0]
    return clean_full_path, clean_bucket_name, clean_key_prefix


def delete_object_s3(s3_resource, bucket, key_prefix, l_object_key):
    full_path, bucket, key_prefix = get_s3_formatted_bucket_path(bucket, key_prefix)
    s3_bucket = s3_resource.Bucket(bucket)
    delete = {
        "Objects": []
    }
    for key in l_object_key:
        delete["Objects"].append({"Key": key_prefix + key})
    return s3_bucket.delete_objects(Delete=delete)
