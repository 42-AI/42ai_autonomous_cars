import elasticsearch_dsl as esdsl
from pathlib import Path
import json

from get_data.utils import es_utils
from get_data.cluster_param import ES_HOST_IP, ES_INDEX, ES_HOST_PORT


def _add_query(search_obj, field, query, bool="match"):
    if "field" in query:
        field = f'{field}.{query["field"]}' if query["field"] != "" else field
        query.pop("field")
    if "bool" in query:
        bool = query["bool"]
        query.pop("bool")
    query_type = query["type"]
    query.pop("type")
    repackage_query = {field: query}
    if bool == "match":
        return search_obj.query(query_type, **repackage_query)
    elif bool == "filter":
        return search_obj.filter(query_type, **repackage_query)
    else:
        print(f'Unknown value for "bool" argument. Got {bool}')
        return None


def get_search_query_from_dict(d_query):
    s = esdsl.Search()
    for field, query in d_query.items():
        if "type" not in query or query["type"] == "": continue
        s = _add_query(s, field, query)
    return s


def run_query(search_obj):
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    s = search_obj.using(using=es, index="patate-db")
    s = s.source(["img_id", "file_name"])
    result = s.execute()
    for pic in result:
        print(pic)
