from get_data import upload_to_db as upload
from get_data import cluster_param
from get_data.utils import s3_utils
from get_data.utils import es_utils


def test_upload_to_db():
    label_file = "get_data/sample/labels.json"
    bucket_name = "032854191254-patate"
    key_prefix = ""
    es_ip_host = cluster_param.ES_HOST_IP
    es_port_host = cluster_param.ES_HOST_PORT
    es_index_name = "test_index"
    success, fail = upload.upload_to_db(label_file, bucket_name, key_prefix, es_ip_host, es_port_host, es_index_name,
                                        overwrite=False)
    assert (success, fail) == (5, 1)


def test_upload_to_db_overwrite():
    label_file = "get_data/sample/labels.json"
    bucket_name = "032854191254-patate"
    key_prefix = ""
    es_ip_host = cluster_param.ES_HOST_IP
    es_port_host = cluster_param.ES_HOST_PORT
    es_index_name = "test_index"
    success, fail = upload.upload_to_db(label_file, bucket_name, key_prefix, es_ip_host, es_port_host, es_index_name,
                                        overwrite=True)
    assert (success, fail) == (5, 1)


def test_upload_to_db_cant_overwrite():
    label_file = "get_data/sample/labels.json"
    bucket_name = "032854191254-patate"
    key_prefix = ""
    es_ip_host = cluster_param.ES_HOST_IP
    es_port_host = cluster_param.ES_HOST_PORT
    es_index_name = "test_index"
    success, fail = upload.upload_to_db(label_file, bucket_name, key_prefix, es_ip_host, es_port_host, es_index_name,
                                        overwrite=False)
    assert (success, fail) == (0, 6)


def test_upload_to_db_key_prefix():
    label_file = "get_data/sample/labels.json"
    bucket_name = "032854191254-patate/"
    key_prefix = "/weird/path//"
    es_ip_host = cluster_param.ES_HOST_IP
    es_port_host = cluster_param.ES_HOST_PORT
    es_index_name = "test_index"
    success, fail = upload.upload_to_db(label_file, bucket_name, key_prefix, es_ip_host, es_port_host, es_index_name,
                                        overwrite=True)
    assert (success, fail) == (5, 1)


def test_upload_to_db_single_label():
    label_file = "get_data/sample/single_label.json"
    bucket_name = "032854191254-patate"
    key_prefix = ""
    es_ip_host = cluster_param.ES_HOST_IP
    es_port_host = cluster_param.ES_HOST_PORT
    es_index_name = "test_index"
    success, fail = upload.upload_to_db(label_file, bucket_name, key_prefix, es_ip_host, es_port_host, es_index_name,
                                        overwrite=True)
    assert (success, fail) == (1, 0)


def test_delete_object_in_s3():
    label_file = "get_data/sample/labels.json"
    bucket_name = "032854191254-patate"
    key_prefix = ""
    l_label = upload.get_label_list_from_file(label_file)
    id_list = [label["img_id"] for label in l_label]
    s3_resource = s3_utils.get_s3_resource()
    ret = s3_utils.delete_object_s3(s3_resource, bucket_name, key_prefix, id_list)
    assert ret["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_delete_object_in_s3_key_prefix():
    label_file = "get_data/sample/labels.json"
    bucket_name = "032854191254-patate"
    key_prefix = "/weird/path//"
    l_label = upload.get_label_list_from_file(label_file)
    id_list = [label["img_id"] for label in l_label]
    s3_resource = s3_utils.get_s3_resource()
    ret = s3_utils.delete_object_s3(s3_resource, bucket_name, key_prefix, id_list)
    assert ret["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_delete_index_es():
    es_ip_host = cluster_param.ES_HOST_IP
    es_port_host = cluster_param.ES_HOST_PORT
    es_index_name = "test_index"
    ret = es_utils.delete_index(es_index_name, es_ip_host, es_port_host)
    assert "acknowledged" in ret and ret["acknowledged"] is True


if __name__ == "__main__":
    test_delete_index_es()

