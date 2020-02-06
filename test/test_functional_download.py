import pytest
import json
from pathlib import Path
import time

from get_data.src import s3_utils, get_from_db, upload_to_db as upload
from get_data.src import es_utils
from conf import cluster_conf


@pytest.fixture
def test_init():
    bucket_name = cluster_conf.BUCKET_NAME
    key_prefix = "test_download"
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    es_index_name = "test_index"
    output_test_folder = Path("output_test_folder")
    output_test_folder.mkdir(exist_ok=True)
    yield output_test_folder, bucket_name, key_prefix, es_ip_host, es_port_host, es_index_name
    print("--------------- Test completed ----------------")
    print("Deleting test pictures from s3")
    s3_utils.delete_all_in_s3_folder(bucket=bucket_name, key_prefix=key_prefix)
    print("Deleting test index")
    es_utils.delete_index(es_index_name, host_ip=cluster_conf.ES_HOST_IP, port=cluster_conf.ES_HOST_PORT)
    print("Deleting test folder...")
    for file in output_test_folder.iterdir():
        file.unlink()
    output_test_folder.rmdir()


def test_download_single_file(test_init):
    label_file = "test/resources/single_label.json"
    output_test_folder, bucket_name, key_prefix, es_ip_host, es_port_host, es_index_name = test_init
    with Path(label_file).open(mode='r', encoding='utf-8') as fp:
        label = json.load(fp)
    first_key = next(iter(label))
    output = Path(output_test_folder) / label[first_key]["file_name"]
    s3_success, es_success, fail = upload.upload_to_db(label_file, bucket_name, es_ip_host, es_port_host, es_index_name,
                                                       key_prefix=key_prefix, overwrite=True)
    if fail > 0:
        raise RuntimeError("Failed to upload to s3, can't test download if upload is not working")
    time.sleep(1)
    test_res = s3_utils.download_from_s3(first_key, f'{bucket_name}/{key_prefix}', output.as_posix())
    assert test_res is None


def test_download_full_pipeline(test_init):
    label_file = "test/resources/labels.json"
    output_test_folder, bucket_name, key_prefix, es_ip_host, es_port_host, es_index_name = test_init
    s3_success, es_success, fail = upload.upload_to_db(label_file, bucket_name, es_ip_host, es_port_host, es_index_name,
                                                       key_prefix=key_prefix, overwrite=True)
    assert fail == 1
    search = {
        "event": {
            "type": "match",
            "field": "",
            "query": "demo_session"
        }
    }
    search_json = "tmp_search_test.json"
    with Path(search_json).open(mode='w', encoding='utf-8') as fp:
        json.dump(search, fp)
    time.sleep(1)
    l_dl_picture = get_from_db.search_and_download(search_json, output_test_folder, es_index=es_index_name, force=True)
    Path(search_json).unlink()
    assert len(l_dl_picture) == 3

