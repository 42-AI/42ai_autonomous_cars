import elasticsearch_dsl as esdsl
from pathlib import Path
import json

from get_data.utils import es_utils
from get_data.cluster_param import ES_HOST_IP, ES_INDEX, ES_HOST_PORT


def _add_query(search_obj, field, query):
    if "field" in query:
        field = f'{field}.{query["field"]}' if query["field"] != "" else field
        query.pop("field")
    query_type = query["type"]
    query.pop("type")
    repackage_query = {field: query}
    return search_obj.query(query_type, **repackage_query)


def create_search_query_from_dict(d_query):
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    s = esdsl.Search(using=es, index="patate-db")
    for field, query in d_query.items():
        if "type" not in query or query["type"] == "": continue
        s = _add_query(s, field, query)
    print(s.to_dict())
    return s
