import pytest

from conf import cluster_conf
from get_data.src import upload_to_db as upload
from get_data.src import update_db
from get_data.src import es_utils
from conf.cluster_conf import ES_HOST_PORT, ES_HOST_IP


ES_TEST_INDEX = "test_index"


@pytest.fixture(scope="function", autouse=True)
def create_test_index():
    es_utils.delete_index(ES_TEST_INDEX, host_ip=cluster_conf.ES_HOST_IP, port=cluster_conf.ES_HOST_PORT)
    es_utils.create_es_index(ES_HOST_IP, ES_HOST_PORT, ES_TEST_INDEX)


def test_upload_to_db_overwrite():
    label_file = "test/resources/labels.json"
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = ""
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=True)
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=True)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (3, 3, 1)


def test_upload_to_db():
    label_file = "test/resources/labels.json"
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = ""
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=False)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (3, 3, 1)


def test_upload_to_db_s3_KO_es_OK():
    label_file = "test/resources/labels.json"
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = ""
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=True)
    es_utils.delete_index(ES_TEST_INDEX, es_ip_host, es_port_host)
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=False)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (0, 3, 4)


def test_upload_to_db_s3_OK_es_KO():
    label_file = "test/resources/labels.json"
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = ""
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=True)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host, s3_only=True)
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=False)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (3, 0, 4)


def test_upload_to_db_cant_overwrite():
    label_file = "test/resources/labels.json"
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = ""
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=True)
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=False)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (0, 0, 7)


def test_upload_to_db_key_prefix():
    label_file = "test/resources/labels.json"
    bucket_name = cluster_conf.BUCKET_NAME + "/"
    key_prefix = "/weird/path//"
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=True)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (3, 3, 1)


def test_upload_to_db_single_label():
    label_file = "test/resources/single_label.json"
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = ""
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=True)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (1, 1, 0)


def test_upload_to_db_es_only():
    label_file = "test/resources/labels.json"
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = ""
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=None, key_prefix=key_prefix, overwrite=True)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (0, 4, 0)


def test_upload_to_db_remove_todelete_label():
    label_file = "test/resources/labels_delete.json"
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = ""
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    s3_success, es_success, fail = upload.upload_to_db(label_file, es_ip_host, es_port_host, ES_TEST_INDEX,
                                                       bucket_name=bucket_name, key_prefix=key_prefix, overwrite=True)
    update_db.delete_pic_and_index(label_file, bucket_name, key_prefix, ES_TEST_INDEX, es_ip_host, es_port_host)
    assert (s3_success, es_success, fail) == (1, 1, 1)
