import elasticsearch_dsl as esdsl
import json
from pathlib import Path
from datetime import datetime
import time

from get_data.src import s3_utils
from get_data.src import es_utils
from get_data.src import utils_fct
from conf.cluster_conf import ES_INDEX, ES_HOST_PORT, ES_HOST_IP, BUCKET_NAME


def _get_img_and_label_to_delete_from_file(label_file):
    d_label = utils_fct.get_label_dict_from_file(label_file)
    if d_label is None:
        return 0, 0
    l_to_delete = utils_fct.remove_label_to_delete_from_dict(d_label)
    l_label_to_delete = [label["label_fingerprint"] for label in l_to_delete]
    l_img_delete = [(label["img_id"], label["s3_key"]) for label in l_to_delete]
    return l_img_delete, l_label_to_delete


def _user_ok_for_deletion(file_name, nb_of_img_to_delete):
    print(f'File "{file_name}" loaded.')
    ok = None
    while ok not in ["y", "n"]:
        ok = input(f'{nb_of_img_to_delete} picture(s) and label(s) will be deleted, to you want to proceed (y/n)? ')
    if ok == "n":
        exit(0)
    return True


def delete_picture_and_label(label_file, es_index=ES_INDEX, bucket=None, force=False):
    """
    Read a labels json file and delete all labels with the key "to_delete" in their dictionary.
    Labels will be removed from Elasticsearch and pictures from S3.
    Pictures in local file will also be removed after user approval.
    For instance, given the following json, picture with "id2" will be removed from S3 bucket "my_s3_bucket" and label
    "8s64fs4g4h51" will be removed from ES.
    {
      "id1": {
        "location": "my_s3_bucket",
        "label_fingerprint": "1asd5g4gdf1s",
        ...
      },
      "id2": {
        "to_delete": "value doesn't matter",
        "location": "my_s3_bucket",
        "label_fingerprint": "8s64fs4g4h51",
      ...
    }
    :param label_file:          [str]   Path to the label file
    :param es_index:            [str]   Elasticsearch index name. By default, index name is read from the config file.
    :param bucket:              [str]   Name of the s3 bucket where to delete the picture. If None (default), bucket
                                        name is read from the label
    :param force:               [bool]  False by default. If True, will proceed with delete without user confirmation.
    :return:                    [tuple] (int, int, int, int):
                                        number of successful delete from Elastic, number of failed delete from ES,
                                        number of successful delete from S3, number of failed delete from S3
    """
    l_img_to_delete, l_label_fingerprint_to_delete = _get_img_and_label_to_delete_from_file(label_file)
    if len(l_img_to_delete) == 0:
        return 0, 0, 0, 0
    if not force and not _user_ok_for_deletion(label_file, len(l_img_to_delete)):
        return 0, 0, 0, 0
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    print(f'Deleting {len(l_img_to_delete)} label(s) in index "{es_index}" ({ES_HOST_IP}:{ES_HOST_PORT})...')
    i_es_success, l_failed_es = es_utils.delete_document(es=es, index=es_index, l_doc_id=l_label_fingerprint_to_delete)
    print(f'{i_es_success} label(s) successfully deleted from index "{es_index}" ({ES_HOST_IP}:{ES_HOST_PORT})')
    time.sleep(1)
    s = esdsl.Search(index=es_index).using(es)
    s3 = s3_utils.get_s3_resource()
    bucket = BUCKET_NAME if bucket is None else bucket
    l_ok_delete = []
    l_failed_s3 = []
    print(f'Deleting {len(l_img_to_delete)} picture(s) in s3...')
    for img_id, s3_key in l_img_to_delete:
        s = s.query("match", img_id=img_id)
        response = s.execute()
        if response.hits.total.value > 0:
            print(f'  --> Image "{img_id}" can\'t be removed: {response.hits.total.value} label(s) points to it.'
                  f' List of labels:')
            blocking_label = [hit.label_fingerprint for hit in response.hits]
            print(f'      {blocking_label}')
            l_failed_s3.append(img_id)
        else:
            if not s3_utils.object_exist_in_bucket(s3=s3, bucket=bucket, key=s3_key):
                print(f'Image with id "{img_id}" couldn\'t be deleted from s3 bucket "{bucket}"'
                      f' because key "{s3_key}" does not exists.')
                l_failed_s3.append(img_id)
            else:
                l_ok_delete.append(s3_key)
    if len(l_ok_delete) > 0:
        s3_utils.delete_object_s3(bucket=bucket, l_object_key=l_ok_delete, s3_resource=s3)
    print(f'Deletions completed: {len(l_failed_es)} delete failed in ES ; {len(l_failed_s3)} delete failed in S3')
    return i_es_success, len(l_failed_es), len(l_img_to_delete) - len(l_failed_s3), len(l_failed_s3)


def delete_pic_and_index(label_file, bucket_name, key_prefix, index, es_ip, es_port, s3_only=False):
    """
    Delete all picture listed in label file from s3 and delete index passed in parameters
    :param label_file:      [str]   Path to the labelfile, json format
    :param bucket_name:     [str]   Name of the bucket containing the pictures
    :param key_prefix:      [str]   key prefix to find the picture
    :param index:           [str]   Index to delete
    :param es_ip:           [str]   Ip of the Elastic host
    :param es_port:         [str]   port opened for Elastic
    :param s3_only:         [bool]  If True, only delete picture from s3
    """
    d_label = utils_fct.get_label_dict_from_file(label_file)
    l_pic_id = list(d_label.keys())
    l_pic_s3_key = [s3_utils.get_s3_formatted_bucket_path(bucket_name, key_prefix, pic_id)[2] for pic_id in l_pic_id]
    s3_utils.delete_object_s3(bucket_name, l_pic_s3_key)
    if not s3_only:
        es_utils.delete_index(index, es_ip, es_port)


def _ask_user_dataset_details(dataset):
    ok = "no"
    while ok != "y":
        ok = "no"
        name = input("Type in the name of the dataset: ")
        comment = input("Type in some comment about this dataset:\n")
        date = datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")
        date_user = None
        while date_user is None:
            date_user = input(f'Created on: {date}. Press enter to validate or type in a new value.\n')
            if date_user != "":
                try:
                    datetime.strptime(date_user, "%Y%m%dT%H-%M-%S-%f")
                    date = date_user
                except ValueError as err:
                    date_user = None
                    print(err)
        dataset["created_on_date"] = date
        dataset["name"] = name
        dataset["comment"] = comment
        print(f'Dataset is :\n{dataset}')
        while ok != "y" and ok != "n":
            ok = input("Are you ok with this dataset (y/n)? ")
    return dataset


def create_dataset(label_json_file, raw_query_file=None, overwrite_input_file=True, es_index=ES_INDEX,
                   es_host_ip=ES_HOST_IP, es_host_port=ES_HOST_PORT):
    """
    Create a dataset interactively and add all the labels in label_json_file to this dataset
    :param label_json_file:             [str]   Path to the input file containing all the labels
    :param raw_query_file:              [str]   Path to the raw query file used to get the labels json from the database
    :param overwrite_input_file:        [bool]  If True (default), the input file will be modified with the new dataset.
                                                Note that however the only truth is the database, your local file might
                                                be out of date.
    :param es_index:                    [str]   Name of the index to update
    :param es_host_ip:                  [str]   ip of the host. If None, value is retrieved from the config file
    :param es_host_port                 [str]   port opened for ES. If None, value is retrieved from the config file
    :return                             [bool]
    """
    d_label = utils_fct.get_label_dict_from_file(label_json_file)
    print(f'{len(d_label)} picture(s) loaded')
    if d_label is None or len(d_label) == 0:
        print(f'Input file "{label_json_file}" is empty.')
        return False
    if raw_query_file is not None:
        with Path(raw_query_file).open(mode='r', encoding='utf-8') as fp:
            dataset = {"query": json.load(fp)}
    else:
        dataset = {"query": None}
    dataset = _ask_user_dataset_details(dataset)
    es_utils.update_doc_in_index(d_label, "dataset", dataset, es_index, es_host_ip, es_host_port)
    if overwrite_input_file:
        for img_id, label in d_label.items():
            if label["dataset"] is None:
                label["dataset"] = [dataset]
            else:
                label["dataset"].append(dataset)
        try:
            with Path(label_json_file).open(mode='w', encoding='utf-8') as fp:
                json.dump(d_label, fp, indent=4)
            print(f'Label file "{label_json_file}" has been updated.')
        except IOError as err:
            print(f'Couldn\'t update "{label_json_file} because : {err}')
    return True
