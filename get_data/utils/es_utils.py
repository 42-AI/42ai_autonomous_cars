import os
import elasticsearch
from elasticsearch import helpers
import elasticsearch_dsl as esdsl
from tqdm import tqdm
import json
from pathlib import Path

from utils.path import INDEX_TEMPLATE


def get_es_session(host_ip, port):
    try:
        user = os.environ["ES_USER_ID"]
        pwd = os.environ["ES_USER_PWD"]
    except KeyError:
        print("  --> Warning: Elasticsearch user and/or password not found. Trying connection without authentication")
        user = ""
        pwd = ""
    try:
        es = elasticsearch.Elasticsearch([{"host": host_ip, "port": port, "timeout": 10}], http_auth=(user, pwd))
        connection_ok = es.ping()
        if not connection_ok:
            print(f'Failed to connect to Elasticsearch cluster "{host_ip}:{port}"')
            return None
    except elasticsearch.ElasticsearchException as err:
        print(f'Failed to connect to Elasticsearch cluster "{host_ip}:{port}" because:\n{err}')
        return None
    return es


def create_patate_db_index(host_ip, host_port, index_name):
    """Create an index in ES from the template defined in utils.path"""
    es = get_es_session(host_ip, host_port)
    if es is None:
        return None
    with Path(INDEX_TEMPLATE).open(mode='r', encoding='utf-8') as fp:
        index_template = json.load(fp)
    es.indices.create(index_name, body=index_template)


def _gen_bulk_doc(l_label, index, op_type):
    """Yield well formatted document for bulk upload to ES"""
    for label in tqdm(l_label):
        yield {
            "_index": index,
            "_type": "_doc",
            "_op_type": op_type,
            "_id": label["img_id"],
            "_source": label
        }


def upload_to_es(l_label, index, host_ip, port, update=False):
    """
    Upload all label in l_label to Elasticsearch cluster.
    Note that credential to access the cluster is retrieved from env variable (see variable name in the code)
    :param l_label:             [list]      List of labels. Each label shall contains the following keys:
                                            "file_name": the name of the picture file
                                            "location": path to the picture directory
                                            "img_id": id that will be used to index the picture (shall be unique)
    :param index:               [string]    Name of the index to use for indexing labels
    :param host_ip:             [string]    Public ip of the Elasticsearch host server
    :param port:                [int]       Port open for Elasticsearch on host server (typically 9200)
    :param update:              [bool]      If True, existing document with same img_id will be overwritten by new ones
    :return:                    [list]      list of failed to upload picture id
    """
    es = get_es_session(host_ip, port)
    if es is None:
        return [label["img_id"] for label in l_label]
    op_type = "index" if update else "create"
    success, errors = helpers.bulk(es, _gen_bulk_doc(l_label, index, op_type), request_timeout=60, raise_on_error=False)
    failed_doc_id = []
    for error in errors:
        for error_type in error:
            failed_doc_id.append(error[error_type]["_id"])
            print(f'  --> Couldn\'t upload document {failed_doc_id[-1]} because:{error[error_type]["error"]["reason"]}')
    return failed_doc_id


def delete_index(index, host_ip, port):
    """Delete index from ES cluster"""
    es = get_es_session(host_ip, port)
    return es.indices.delete(index=index, ignore=[400, 404])


def delete_document(index, doc_id, es=None, host_ip=None, port=9200):
    if isinstance(doc_id, list):
        print("Bulk delete not yet implemented... sorry, list of doc_id not accepted yet :/")
        exit(1)
    if bool(es) == bool(host_ip):
        print("host_ip and port will be ignored since es session object is provided")
    if es is None:
        es = get_es_session(host_ip, port)
    return es.delete(index=index, id=doc_id, refresh=True)


def _add_query(search_obj, field, query, bool="match"):
    """Add a query to the existing seach obj"""
    if "field" in query:
        field = f'{field}.{query["field"]}' if query["field"] != "" else field
        query.pop("field")
    if "bool" in query:
        bool = query["bool"]
        query.pop("bool")
    query_type = query["type"]
    query.pop("type")
    repackage_query = {field: query}
    if bool == "match" or bool == "must":
        return search_obj.query(query_type, **repackage_query)
    elif bool == "filter":
        return search_obj.filter(query_type, **repackage_query)
    else:
        print(f'Unknown value for "bool" argument. Got {bool}')
        return None


def get_search_query_from_dict(es_index, d_query):
    """
    Takes a dictionary describing a search and return the equivalent search object.
    Expected search dictionary:
    {
        "field_name": {         # name of the field we are searching (e.g.: "event")
            "type": "match",    # search type (eg: "range", "match", ..etc)
            "field": "keyword", # OPTIONAL: subfield for the search (eg: "keyword", "analyzed", ...etc)
            "bool": "filter",   # OPTIONAL: specify the bool operator (eg: "filter", "must", "should", ..etc)
            # Other field depends on the "type" field value. Those fields are exactly those expected by Elasticsearch
             for this type of query. See Elasticsearch documentation.
            # For example, for a "range" search field could be:
            "gte": "20200119"
            "lte": "20210215"
        },
        "field_name_2": {...},
        ...
    }
    :param es_index:        [string]    Name of the index to search in
    :param d_query:         [dict]      Search description dictionary
    :return:                [object]    Elasticsearch-dsl search object
    """
    s = esdsl.Search(index=es_index)
    for field, query in d_query.items():
        if "type" not in query or query["type"] == "": continue
        s = _add_query(s, field, query)
    return s


def run_query(es, search_obj):
    """
    Run the query defined by the 'search_obj' on the Elasticsearch cluster defined by 'es'.
    :param es:              [object]    Elasticsearch session
    :param search_obj:      [object]    Elasticsearch-dsl search object
    :return:                [object]    Elasticsearch-dsl response object
    """
    s = search_obj.using(es)
    s = s.source(["img_id", "file_name", "location"])
    s = s[0:10000]
    return s.execute()
