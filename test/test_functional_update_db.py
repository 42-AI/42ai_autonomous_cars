import pytest
import shutil
from pathlib import Path
import subprocess


from get_data.src import update_db
from get_data.src import upload_to_db
from get_data.src import es_utils
from get_data.src import s3_utils
from get_data.src import utils_fct
from conf.cluster_conf import ES_HOST_PORT, ES_HOST_IP, BUCKET_NAME


ES_TEST_INDEX = "test_index"
LABELS = "test/resources/labels.json"
LABELS_DELETE = "test/resources/labels_delete.json"
LABELS_BLOCK_DELETE = "test/resources/labels_block_delete.json"
TMP_LABELS = "test/.tmp/labels.json"
TMP_LABELS_DELETE = "test/.tmp/labels_delete.json"
KEY_PREFIX = "unittest"
WRONG_KEY_PREFIX = "wrong_key_prefix"


@pytest.fixture(scope="function", autouse=True)
def create_and_delete_test_index():
    es_utils.delete_index(ES_TEST_INDEX, host_ip=ES_HOST_IP, port=ES_HOST_PORT)
    es_utils.create_es_index(ES_HOST_IP, ES_HOST_PORT, ES_TEST_INDEX)
    yield True
    update_db.delete_pic_and_index(LABELS, BUCKET_NAME, KEY_PREFIX, ES_TEST_INDEX, ES_HOST_IP, ES_HOST_PORT)
    update_db.delete_pic_and_index(LABELS, BUCKET_NAME, WRONG_KEY_PREFIX, ES_TEST_INDEX, ES_HOST_IP, ES_HOST_PORT)


@pytest.fixture(scope="function")
def create_delete_tmp_folder():
    shutil.rmtree("test/.tmp", ignore_errors=True)
    shutil.copytree("test/resources", "test/.tmp")
    yield True
    shutil.rmtree("test/.tmp", ignore_errors=True)


def test_delete_pic_and_label_local_delete_false(create_delete_tmp_folder):
    total_file_in_tmp = len(list(Path("test/.tmp").iterdir()))
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(TMP_LABELS_DELETE,
                                                                                  es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME,
                                                                                  force=True,
                                                                                  delete_local=False)
    assert total_file_in_tmp == len(list(Path("test/.tmp").iterdir()))


def test_delete_pic_and_label_local_delete_true(create_delete_tmp_folder):
    assert (Path(TMP_LABELS_DELETE).parent / "20200204T15-23-08-574348.jpg").is_file()
    assert (Path(TMP_LABELS_DELETE).parent / "20200204T15-23-08-695024.jpg").is_file()
    total_file_in_tmp = len(list(Path("test/.tmp").iterdir()))
    upload_to_db.upload_to_db(TMP_LABELS, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=KEY_PREFIX)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(TMP_LABELS_DELETE,
                                                                                  es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME,
                                                                                  force=True,
                                                                                  delete_local=True)
    assert total_file_in_tmp - 2 == len(list(Path("test/.tmp").iterdir()))
    assert not (Path(TMP_LABELS_DELETE).parent / "20200204T15-23-08-574348.jpg").is_file()
    assert not (Path(TMP_LABELS_DELETE).parent / "20200204T15-23-08-695024.jpg").is_file()


def test_delete_pic_and_label_local_delete_true_pic_not_in_db(create_delete_tmp_folder):
    assert (Path(TMP_LABELS_DELETE).parent / "20200204T15-23-08-574348.jpg").is_file()
    assert (Path(TMP_LABELS_DELETE).parent / "20200204T15-23-08-695024.jpg").is_file()
    total_file_in_tmp = len(list(Path("test/.tmp").iterdir()))
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(TMP_LABELS_DELETE,
                                                                                  es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME,
                                                                                  force=True,
                                                                                  delete_local=True)
    assert total_file_in_tmp - 2 == len(list(Path("test/.tmp").iterdir()))
    assert not (Path(TMP_LABELS_DELETE).parent / "20200204T15-23-08-574348.jpg").is_file()
    assert not (Path(TMP_LABELS_DELETE).parent / "20200204T15-23-08-695024.jpg").is_file()


def test_delete_pic_and_label():
    upload_to_db.upload_to_db(LABELS, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=KEY_PREFIX)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(LABELS_DELETE, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (2, 0, 2, 0) == (success_es, fail_es, success_s3, fail_s3)


def test_delete_pic_and_label_wrong_key_prefix():
    upload_to_db.upload_to_db(LABELS, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=WRONG_KEY_PREFIX)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(LABELS_DELETE, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (2, 0, 0, 2) == (success_es, fail_es, success_s3, fail_s3)


def test_delete_pic_and_label_other_label_points_to_pic():
    upload_to_db.upload_to_db(LABELS, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=KEY_PREFIX)
    upload_to_db.upload_to_db(LABELS_BLOCK_DELETE, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(LABELS_DELETE, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (2, 0, 1, 1) == (success_es, fail_es, success_s3, fail_s3)


def test_delete_pic_and_label_nothing_to_delete():
    upload_to_db.upload_to_db(LABELS, es_index=ES_TEST_INDEX, es_host_ip=ES_HOST_IP, es_port=ES_HOST_PORT,
                              bucket_name=BUCKET_NAME, key_prefix=KEY_PREFIX)
    success_es, fail_es, success_s3, fail_s3 = update_db.delete_picture_and_label(LABELS, es_index=ES_TEST_INDEX,
                                                                                  bucket=BUCKET_NAME, force=True,
                                                                                  delete_local=False)
    assert (0, 0, 0, 0) == (success_es, fail_es, success_s3, fail_s3)
