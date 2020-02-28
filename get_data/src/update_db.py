import elasticsearch_dsl as esdsl
import json
from pathlib import Path
from datetime import datetime
import time

from get_data.src import s3_utils
from get_data.src import es_utils
from get_data.src import utils_fct
from get_data.src import get_from_db
from conf.cluster_conf import ES_INDEX, ES_HOST_PORT, ES_HOST_IP, BUCKET_NAME


def _get_img_and_label_to_delete_from_file(label_file):
    d_label = utils_fct.get_label_dict_from_file(label_file)
    if d_label is None:
        return 0, 0
    l_to_delete = utils_fct.remove_label_to_delete_from_dict(d_label)
    l_label_to_delete = [label["label_fingerprint"] for label in l_to_delete]
    l_img_delete = [(label["img_id"], label["s3_key"]) for label in l_to_delete]
    return l_img_delete, l_label_to_delete


def _user_ok_for_deletion(file_name, nb_of_img_to_delete, delete_local=False, label_only=False):
    print(f'File "{file_name}" loaded.')
    ok = None
    while ok not in ["y", "n"]:
        print(f'{nb_of_img_to_delete} ', end="")
        if not label_only:
            print(f'picture(s) and ', end="")
        print(f'label(s) will be deleted from the DB', end="")
        if delete_local:
            print(f' (pictures will also be deleted from your local drive)', end="")
        print(f'. Do you want to proceed (y/n)? ', end="")
        ok = input()
    if ok == "n":
        exit(0)
    return True


def _delete_local_picture(l_pic_id, folder, extension_pattern=".*", verbose=1):
    """
    Delete pictures in local drive
    :param l_pic_id:                [list]  List of picture id (as a string)
    :param folder:                  [str]   Path to the folder containing the pictures
    :param extension_pattern:       [str]   Pattern to append to the pic_id to match with local file. All match will be
                                            deleted. For ex:
                                            folder has file ["123.jpeg", "123.jpg", "123.png"]
                                            pic_id = "123", extenstion_pattern=".jp*" --> "123.jpg" and "123.jpeg" will
                                            be deleted
    :param verbose:                 [int]   verbosity level
    :return:                        [int]   Number of file deleted
    """
    folder = Path(folder)
    cpt_delete = 0
    for pic_id in l_pic_id:
        for pic_file in folder.glob(f'{pic_id}{extension_pattern}'):
            pic_file.unlink()
            if verbose > 0:
                print(f'File "{pic_file}" has been deleted.')
            cpt_delete += 1
    return cpt_delete


def delete_label_only(label_file, es_index=ES_INDEX, force=False):
    """
    Read a labels json file and delete all labels in this file from the database
    :param label_file:      [string]    Path to the input json file
    :param es_index:        [string]    Name of the ES index
    :param force:           [bool]      If True, user won't be prompted for validation before deletion
    :return:                [tuple]     (int, int): nb_of_deletion, nb_of_failed_delete
    """
    d_label = utils_fct.get_label_dict_from_file(label_file)
    l_label_fingerprint = [label["label_fingerprint"] for _, label in d_label.items()]
    if not force and not _user_ok_for_deletion(label_file, len(l_label_fingerprint), label_only=True):
        return 0, 0
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    print(f'Deleting {len(l_label_fingerprint)} label(s) in index "{es_index}" ({ES_HOST_IP}:{ES_HOST_PORT})...')
    i_es_success, l_failed_es = es_utils.delete_document(es=es, index=es_index, l_doc_id=l_label_fingerprint)
    print(f'{i_es_success} label(s) successfully deleted from index "{es_index}" ({ES_HOST_IP}:{ES_HOST_PORT})')
    print(f'{len(l_failed_es)} deletion(s) failed.')
    return i_es_success, l_failed_es


def delete_picture_and_label(label_file, es_index=ES_INDEX, bucket=BUCKET_NAME, force=False, delete_local=False):
    """
    Read a labels json file and delete all labels with the key "to_delete" set to True in their dictionary.
    Labels will be removed from Elasticsearch and pictures from S3.
    Pictures in local file will also be removed after user approval.
    For instance, given the following json, picture with "id2" will be removed from S3 bucket "my_s3_bucket" and label
    "8s64fs4g4h51" will be removed from ES.
    {
      "id1": {
        "s3_bucket": "my_s3_bucket",
        "label_fingerprint": "1asd5g4gdf1s",
        ...
      },
      "id2": {
        "to_delete": "true",
        "s3_bucket": "my_s3_bucket",
        "label_fingerprint": "8s64fs4g4h51",
      ...
    }
    :param label_file:          [str]   Path to the label file
    :param es_index:            [str]   Elasticsearch index name. By default, index name is read from the config file.
    :param bucket:              [str]   Name of the s3 bucket where to delete the picture. If None only labels will be
                                        deleted. Bucket name default value is read from the conf file.
    :param force:               [bool]  False by default. If True, will proceed with delete without user confirmation.
    :param delete_local         [bool]  If True picture will also be deleted from local drive
    :return:                    [tuple] (int, int, int, int):
                                        number of successful delete from Elastic, number of failed delete from ES,
                                        number of successful delete from S3, number of failed delete from S3
    """
    l_img_to_delete, l_label_fingerprint_to_delete = _get_img_and_label_to_delete_from_file(label_file)
    if len(l_img_to_delete) == 0:
        return 0, 0, 0, 0
    if not force and not _user_ok_for_deletion(label_file, len(l_img_to_delete), delete_local, label_only=not bool(bucket)):
        return 0, 0, 0, 0
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    print(f'Deleting {len(l_img_to_delete)} label(s) in index "{es_index}" ({ES_HOST_IP}:{ES_HOST_PORT})...')
    i_es_success, l_failed_es = es_utils.delete_document(es=es, index=es_index, l_doc_id=l_label_fingerprint_to_delete)
    print(f'{i_es_success} label(s) successfully deleted from index "{es_index}" ({ES_HOST_IP}:{ES_HOST_PORT})')
    time.sleep(1)
    l_ok_delete = []
    l_failed_s3 = []
    nb_local_pic_deleted = 0
    if bucket is not None:
        s = esdsl.Search(index=es_index).using(es)
        s3 = s3_utils.get_s3_resource()
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
        if delete_local:
            nb_local_pic_deleted = _delete_local_picture(l_pic_id=[pic_id for pic_id, _ in l_img_to_delete],
                                                         folder=Path(label_file).parent, extension_pattern=".*")
    print(f'Deletions completed:')
    print(f'ES: {i_es_success} deletion(s) ; {len(l_failed_es)} failed.')
    print(f'S3: {len(l_ok_delete)} deletion(s) ; {len(l_failed_s3)} failed')
    print(f'{nb_local_pic_deleted} picture(s) deleted from local drive.')
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
    if d_label is None or len(d_label) == 0:
        if d_label is not None:
            print(f'Input file "{label_json_file}" is empty.')
        return False
    print(f'{len(d_label)} picture(s) loaded')
    if raw_query_file is not None:
        with Path(raw_query_file).open(mode='r', encoding='utf-8') as fp:
            dataset = {"query": json.load(fp)}
    else:
        dataset = {"query": None}
    dataset = _ask_user_dataset_details(dataset)
    es_utils.append_value_to_field(d_label, "dataset", dataset, es_index, es_host_ip, es_host_port)
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


def delete_dataset(dataset_name, es_index=ES_INDEX, es_host_ip=ES_HOST_IP, es_host_port=ES_HOST_PORT, verbose=1,
                   force=False):
    """
    Delete a dataset from the database. All labels with this dataset name in their "dataset.name" field will be updated.
    No labels nor pictures are removed, only the dataset field of the labels is updated.
    :param dataset_name:                [str]   Name of the dataset to delete from the database
    :param es_index:                    [str]   Name of the index to update
    :param es_host_ip:                  [str]   ip of the host. If None, value is retrieved from the config file
    :param es_host_port                 [str]   port opened for ES. If None, value is retrieved from the config file
    :param verbose:                     [int]   verbosity level
    :param force:                       [bool]  If True, user won't be prompt for validation before deleting the dataset
    :return                             [bool]
    """
    search_query = {
        "dataset.name": {
            "type": "match",
            "field": "keyword",
            "query": dataset_name
        }
    }
    d_label = get_from_db.run_search_query(search_query, es_index=es_index, verbose=0)
    if len(d_label) == 0:
        print(f'No labels found for dataset "{dataset_name}".')
        return True
    _, first_doc = next(iter(d_label.items()))
    l_dataset = first_doc["dataset"]
    for dataset in l_dataset:
        if dataset["name"] == dataset_name:
            break
    else:
        print("Dataset not found in result...")
        exit(1)
    print(f'Dataset is : {dataset}')
    validation = "" if not force else "y"
    while validation not in ["y", "n"]:
        validation = input(f'{len(d_label)} labels found in this dataset. Do you want to delete this dataset (y/n)? ')
    es_utils.delete_value_from_field(d_label, "dataset", dataset, es_index, es_host_ip, es_host_port)
