import os
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def get_es_session(host_ip, port):
    try:
        user = os.environ["ES_USER_ID"]
        pwd = os.environ["ES_USER_PWD"]
    except KeyError as err:
        print("  --> Warning: Elasticsearch 'user' and/or password not found. Trying connection without authentication")
        user = ""
        pwd = ""
    es = Elasticsearch([{"host": host_ip, "port": port}], http_auth=(user, pwd))
    return es


def gen_bulk_doc(l_label, index, op_type):
    """Yield well formatted document for bulk upload to ES"""
    for label in l_label:
        yield {
            "_index": index,
            "_type": "document",
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
    op_type = "index" if update else "create"
    success, errors = helpers.bulk(es, gen_bulk_doc(l_label, index, op_type), request_timeout=60, raise_on_error=False)
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
