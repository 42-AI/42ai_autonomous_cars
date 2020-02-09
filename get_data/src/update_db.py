import elasticsearch_dsl as esdsl
import json
from pathlib import Path
from datetime import datetime

from get_data.src import s3_utils
from get_data.src import es_utils
from get_data.src import utils_fct
from conf.cluster_conf import ES_INDEX, ES_HOST_PORT, ES_HOST_IP


def delete_list_of_picture_by_id(l_picture_id, bucket_path, es_index=ES_INDEX):
    s3 = s3_utils.get_s3_resource()
    bucket, key_prefix, file_name = s3_utils.split_s3_path(bucket_path)
    s3_utils.delete_object_s3(s3_resource=s3, bucket=bucket, key_prefix=key_prefix, l_object_key=l_picture_id)
    print(f'Picture "{l_picture_id}" successfully deleted or not found in s3 bucket ({bucket_path})')
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    for pic_id in l_picture_id:
        search = esdsl.Search(index=es_index).query("match", **{"img_id": pic_id})
        search = search.using(es)
        print(f'search is : |{search.to_dict()}|')
        response = search.delete()
        print(f'Picture "{pic_id}" successfully deleted or not found in ES "{es_index}" index '
              f'({response["deleted"]} element(s) deleted)')


def delete_picture(label_file, bucket_path=None, es_index=ES_INDEX):
    """
    Delete all the picture listed in a label file, json format. Label file shall have the following format:
    {
      "id": {
        "location": "s3_bucket_path",
        ...
      },
      ...
    }
    :param label_file:          [str]   Path to the label file
    :param bucket_path:         [str]   bucket name + key prefix if any.
                                        If not defined, the bucket path will be read from the label file. In this case,
                                        the bucket path will be read from the first item in the label file
                                        (thus all items in the file are supposed to be in the same bucket)
    :param es_index:            [str]   Elasticsearch index name
    """
    with Path(label_file).open(mode='r', encoding='utf-8') as fp:
        d_label = json.load(fp)
    l_pic_id = list(d_label.keys())
    if bucket_path is None:
        bucket_path = d_label[l_pic_id[0]]["location"]
    delete_list_of_picture_by_id(l_picture_id=l_pic_id, bucket_path=bucket_path, es_index=es_index)


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
            ok = input("Are ok with this dataset (y/n)? ")
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
