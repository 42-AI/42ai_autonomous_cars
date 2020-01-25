import elasticsearch_dsl as esdsl

from get_data.utils import es_utils
from get_data.cluster_param import ES_HOST_IP, ES_INDEX, ES_HOST_PORT


def create_search(es, index):
    return esdsl.Search(using=es, index=index)


def add_search_query(search_obj, s_type, query):
    search_obj.query(s_type, **query)


def get_search_param(dictionary):
    es = es_utils.get_es_session(host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    s = esdsl.Search(using=es, index="patate-db").query("match", **{"event": "test"})
    s = s.query("range", **{"time": {"gt": 10}})
    s.query("match", **{"timestamp": "10/20/2020"})
    print(s.to_dict())
    exit()
    for key in dictionary:
        if "type" in dictionary[key]:
            add_search_query(s, dictionary[key])
            return
        search_field = key
        search_param = dictionary[key]

