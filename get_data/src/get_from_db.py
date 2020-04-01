from pathlib import Path
import json
from tqdm import tqdm
from datetime import datetime

from get_data.src import es_utils
from get_data.src import s3_utils
from get_data.src import utils_fct
from conf.cluster_conf import ES_INDEX, ES_HOST_IP, ES_HOST_PORT


def _get_missing_picture(picture_dir, d_wanted_pic):
    """
    Look in 'picture_dir' for the pictures listed in 'd_wanted_pic'.
    Return the list of missing pic id.
    :param picture_dir:         [string]        Path to the directory where to look for the pictures
    :param d_wanted_pic:        [dict]          Dictionary of wanted pictures. For each element of this dictionary:
                                                The key is the picture id ("img_id").
                                                The value is a dictionary with at least those 3 keys:
                                                "img_id": {
                                                    "img_id": "id",
                                                    "file_name": "pic_file_name.jpg",
                                                    "s3_bucket": "s3_bucket_path"
                                                }
    :return:                    [dict]          Dictionary of missing picture, same format as d_wanted_pic
    """
    picture_dir = Path(picture_dir)
    l_missing_pic = {}
    for img_id, wanted_pic in d_wanted_pic.items():
        pic_path = picture_dir / wanted_pic["file_name"]
        if not pic_path.is_file():
            l_missing_pic[img_id] = wanted_pic
    return l_missing_pic


def run_search_query(d_query, es_index=ES_INDEX, verbose=1):
    """
    Search labels in the database according to a json_file describing the query and return the list of matching labels.
    :param d_query:         [string]        Dictionary containing the query
    :param es_index:        [string]        Name of the index
    :param verbose:         [int]           verbosity level
    :return:                [dict]          Dictionary of labels as follow, or None on error.
                                            {
                                                img_id: {
                                                    "img_id": id,
                                                    "file_name": "pic_file_name.jpg",
                                                    "s3_bucket": "s3_bucket_path",
                                                    ...
                                                },
                                                ...
                                            }
    """
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    if es is None:
        return None
    search_obj = es_utils.get_search_query_from_dict(es_index, d_query)
    response = es_utils.run_query(es, search_obj)
    if verbose > 0:
        print(f'Query sent to {ES_HOST_IP}:{ES_HOST_PORT}')
        if verbose > 1:
            print(f'{search_obj.to_dict()}')
        print(f'Query return successfully: {response.success()}')
    if response.hits.total.relation != "eq":
        print(f'WARNING --> you hit the maximum number of result limits: the picture list might not be complete.')
    d_match_pic = {}
    for hit in response.to_dict()["hits"]["hits"]:
        img_id = hit["_source"]["img_id"]
        if img_id in d_match_pic:
            fingerprint_1 = hit["_source"]["label_fingerprint"]
            fingerprint_2 = d_match_pic[img_id]["label_fingerprint"]
            print(f'WARNING --> Your search return multiple label for a single picture: Labels "{fingerprint_1}" '
                  f'and "{fingerprint_2}" point to the same picture: "{img_id}". Only one label will be saved.')
        d_match_pic[img_id] = hit["_source"]
    return d_match_pic


def run_search_query_from_file(query_file, es_index=ES_INDEX, verbose=1):
    """
    Search labels in the database according to a json_file describing the query and return the list of matching labels.
    :param query_file:      [string]        Path to the search description file, json format
    :param es_index:        [string]        Name of the index
    :param verbose:         [int]           verbosity level
    :return:                [dict]          Dictionary of labels as follow, or None on error.
                                            {
                                                img_id: {
                                                    "img_id": id,
                                                    "file_name": "pic_file_name.jpg",
                                                    "s3_bucket": "s3_bucket_path",
                                                    ...
                                                },
                                                ...
                                            }
    """
    with Path(query_file).open(mode='r', encoding='utf-8') as fp:
        d_query = json.load(fp)
    return run_search_query(d_query, es_index=es_index, verbose=verbose)


def _write_labels_to_file(output, d_label, verbose=1):
    """Write d_label to the output file"""
    with Path(output).open(mode='w', encoding='utf-8') as fp:
        json.dump(d_label, fp, indent=4)
        if verbose > 0:
            print(f'Labels written to: "{Path(output)}"')


def search_and_download(query_json, picture_dir, label_file_name="labels.json", es_index=ES_INDEX, force=False, verbose=1):
    """
    Search picture in the database according to a query_json file describing the query and download the picture
    not found in the picture_dir. Missing pictures are download to this same picture_dir.
    A picture is missing if the "file_name", as stored in the db, can't be found in picture_dir.
    :param query_json:      [string]        Path to the search description file, json format
    :param picture_dir:     [string]        Path to the picture directory
    :param label_file_name  [string]        Name of the json file for writing the label of the pictures.
                                            If file name already exists in 'picture_dir', a new name will be generated.
    :param es_index:        [string]        Name of the index
    :param force:           [int]           If True, will NOT prompt user for validation before download.
    :param verbose:         [int]           Verbosity level
    :return:                [dict]          Dictionary of downloaded pictures as follow:
                                            {
                                                img_id: {
                                                    "img_id": id,
                                                    "file_name": "pic_file_name.jpg",
                                                    "s3_bucket": "s3_bucket_path"
                                                },
                                                ...
                                            }
                            [None]          Return None on error.
    """
    picture_dir = Path(picture_dir)
    if not picture_dir.is_dir():
        picture_dir.mkdir(parents=True)
        print(f'Output folder "{picture_dir}" created.')
    label_file_name = utils_fct.get_label_file_name(directory=picture_dir, base_name="labels")
    print(f'Searching for picture in "{es_index}" index')
    d_matching_label = run_search_query_from_file(query_file=query_json, es_index=es_index, verbose=verbose)
    if d_matching_label is None:
        return None
    if len(d_matching_label) == 0:
        print(f'No matching picture found.')
        return {}
    _write_labels_to_file(output=label_file_name, d_label=d_matching_label)
    d_missing_pic = _get_missing_picture(picture_dir, d_matching_label)
    print(f'{len(d_matching_label)} picture(s) found matching the query')
    print(f'{len(d_missing_pic)} picture(s) missing in "{picture_dir}"')
    if len(d_missing_pic) == 0:
        return []
    if not force:
        proceed = None
        while proceed not in ["y", "n"]:
            proceed = input(f'Do you want to proceed and download the {len(d_missing_pic)} missing picture(s) (y/n)? ')
        if proceed == "n":
            return []
    print("Downloading the missing picture(s)...")
    s3_utils.download_from_s3(d_missing_pic, output_dir=picture_dir)
    return d_missing_pic
