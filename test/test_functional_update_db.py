import pytest
from pathlib import Path
import subprocess


from get_data.src import update_db
from get_data.src import upload_to_db
from get_data.src import es_utils
from conf.cluster_conf import ES_HOST_PORT, ES_HOST_IP, BUCKET_NAME


ES_TEST_INDEX = "test_index"


@pytest.fixture(scope="function", autouse=True)
def create_test_index():
    es_utils.delete_index(ES_TEST_INDEX, host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    es_utils.create_es_index(ES_HOST_IP, ES_HOST_PORT, ES_TEST_INDEX)


def test_delete_pic_and_label():
    file = "test/resources/labels.json"
    file_delete = "test/resources/labels_delete.json"
    key_prefix = "resources"
    upload_to_db.upload_to_db(file, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=key_prefix)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(file_delete, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (2, 0, 2, 0) == (success_es, fail_es, success_s3, fail_s3)
    update_db.delete_pic_and_index(file, BUCKET_NAME, key_prefix, ES_TEST_INDEX, ES_HOST_IP, ES_HOST_PORT)


def test_delete_pic_and_label_wrong_key_prefix():
    file = "test/resources/labels.json"
    file_delete = "test/resources/labels_delete.json"
    key_prefix = "wrong_key_prefix"
    upload_to_db.upload_to_db(file, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=key_prefix)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(file_delete, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (2, 0, 0, 2) == (success_es, fail_es, success_s3, fail_s3)
    update_db.delete_pic_and_index(file, BUCKET_NAME, key_prefix, ES_TEST_INDEX, ES_HOST_IP, ES_HOST_PORT)


def test_delete_pic_and_label_other_label_points_to_pic():
    file = "test/resources/labels.json"
    file_delete = "test/resources/labels_delete.json"
    file_blocking_label = "test/resources/labels_block_delete.json"
    key_prefix = "resources"
    upload_to_db.upload_to_db(file, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=key_prefix)
    upload_to_db.upload_to_db(file_blocking_label, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(file_delete, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (2, 0, 1, 1) == (success_es, fail_es, success_s3, fail_s3)
    update_db.delete_pic_and_index(file, BUCKET_NAME, key_prefix, ES_TEST_INDEX, ES_HOST_IP, ES_HOST_PORT)


def test_delete_pic_and_label_nothing_to_delete():
    file = "test/resources/labels.json"
    key_prefix = "wrong_key_prefix"
    upload_to_db.upload_to_db(file, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=key_prefix)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(file, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (0, 0, 0, 0) == (success_es, fail_es, success_s3, fail_s3)
    update_db.delete_pic_and_index(file, BUCKET_NAME, key_prefix, ES_TEST_INDEX, ES_HOST_IP, ES_HOST_PORT)


def test_delete_pic_and_label_local_delete_true():
    """
    subprocess.call("test/resources/copy_to_tmp.sh")
    file = "test/.tmp/labels.json"
    file_delete = "test/.tmp/labels_delete.json"
    key_prefix = "resources"
    upload_to_db.upload_to_db(file, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=key_prefix)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(file_delete, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (2, 0, 2, 0) == (success_es, fail_es, success_s3, fail_s3)
    update_db.delete_pic_and_index(file, BUCKET_NAME, key_prefix, ES_TEST_INDEX, ES_HOST_IP, ES_HOST_PORT)
    """
