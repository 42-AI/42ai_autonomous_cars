from pathlib import Path
import json

from get_data.utils import es_utils
from get_data.cluster_param import ES_INDEX, ES_HOST_IP, ES_HOST_PORT


def find_picture(json_file, output=None):
    """
    Search picture in the database according to the json_file.
    :param json_file:       [string]    Path to the search description file, json format
    :param output:          [string]    Path to file where to save the list of picture
    :return:                [list]      List of tuple: (img_id, file_name)
    """
    with Path(json_file).open(mode='r', encoding='utf-8') as fp:
        d_query = json.load(fp)
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    s = es_utils.get_search_query_from_dict(ES_INDEX, d_query)
    response = es_utils.run_query(es, s)
    print(f'Query return successfully: {response.success()}')
    print(f'Total number of pictures found {"=" if response.hits.total.relation == "eq" else ">"} '
          f'{response.hits.total.value}')
    list_of_pic = [(pic.img_id, pic.file_name) for pic in response]
    print(list_of_pic)
    if output is not None:
        with Path(output).open(mode='w', encoding='utf-8') as fp:
            json.dump(list_of_pic, fp)
        print(f'Result written to "{Path(output)}"')
    return list_of_pic
