from pathlib import Path
import json
from tqdm import tqdm
from datetime import datetime

from get_data.src import es_utils
from get_data.src import s3_utils
from get_data.src import utils_fct
from conf.cluster_conf import ES_INDEX, ES_HOST_IP, ES_HOST_PORT


def get_missing_picture(picture_dir, d_wanted_pic):
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
                                                    "location": "s3_bucket_path"
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


def find_picture_in_db(json_file, output=None, es_index=ES_INDEX, verbose=1):
    """
    Search picture in the database according to a json_file describing the query and return the list of matching pics.
    :param json_file:       [string]        Path to the search description file, json format
    :param output:          [string]        Path to directory where to write the output as a json.
    :param es_index:        [string]        Name of the index
    :param verbose:         [int]           verbosity level
    :return:                [dict]          Dictionary of pictures as dictionary as follow:
                                            {
                                                img_id: {
                                                    "img_id": id,
                                                    "file_name": "pic_file_name.jpg",
                                                    "location": "s3_bucket_path"
                                                },
                                                ...
                                            }
                            [None]          Return None on error.
    """
    with Path(json_file).open(mode='r', encoding='utf-8') as fp:
        d_query = json.load(fp)
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
        print(f'WARNING: you hit the maximum number of result limits: the picture list might not be complete.')
    # list_of_pic = [{"img_id": pic.img_id, "file_name": pic.file_name, "location": pic.location} for pic in response]
    d_match_pic = dict([(hit["_source"]["img_id"], hit["_source"]) for hit in response.to_dict()["hits"]["hits"]])
    if output is not None and len(d_match_pic) > 0:
        with Path(output).open(mode='w', encoding='utf-8') as fp:
            json.dump(d_match_pic, fp, indent=4)
        if verbose > 0:
            print(f'Labels written to: "{Path(output)}"')
    return d_match_pic


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
                                                    "location": "s3_bucket_path"
                                                },
                                                ...
                                            }
                            [None]          Return None on error.
    """
    picture_dir = Path(picture_dir)
    label_file_name = picture_dir / label_file_name
    if not picture_dir.is_dir():
        picture_dir.mkdir(parents=True)
        print(f'Output folder "{picture_dir}" created.')
    elif label_file_name.is_file():
        label_file_name = utils_fct.get_label_file_name(label_file_name)
    print(f'Searching for picture in "{es_index}" index')
    d_matching_label = find_picture_in_db(json_file=query_json, es_index=es_index, verbose=verbose,
                                          output=label_file_name)
    if d_matching_label is None or len(d_matching_label) == 0:
        return None
    d_missing_pic = get_missing_picture(picture_dir, d_matching_label)
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
    for img_id, picture in tqdm(d_missing_pic.items()):
        output_file = picture_dir / picture["file_name"]
        s3_utils.download_from_s3(img_id, picture["location"], output_file.as_posix())
    print(f'Pictures have successfully been downloaded to "{picture_dir}"')
    return d_missing_pic
