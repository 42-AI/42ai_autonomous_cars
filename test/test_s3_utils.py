from datetime import datetime

from get_data.src import s3_utils
from get_data.src import upload_to_db as upload


def test_is_valid_s3_key_simple():
    check, regex = s3_utils.is_valid_s3_key("test")
    assert check is True


def test_is_valid_s3_key_all_valid_char():
    check, regex = s3_utils.is_valid_s3_key("s3-valid_key/nothing(should)match*here!/bu'cket")
    assert check is True


def test_is_valid_s3_key_invalid_char1():
    check, regex = s3_utils.is_valid_s3_key("s3-valid@key/nothing(should)match*here!/bu'cket")
    assert check is False


def test_is_valid_s3_key_invalid_char2():
    check, regex = s3_utils.is_valid_s3_key("s3-valid key/nothing(should)match*here!/bu'cket")
    assert check is False


def test_is_valid_s3_key_invalid_char3():
    check, regex = s3_utils.is_valid_s3_key("s3-valid%key/nothing(should)match*here!/bu'cket")
    assert check is False


def test_is_valid_s3_key_invalid_char4():
    check, regex = s3_utils.is_valid_s3_key("s3-valid#key/nothing(should)match*here!/bu'cket")
    assert check is False


def test_is_valid_s3_key_invalid_char5():
    check, regex = s3_utils.is_valid_s3_key("s3-valid&key/nothing(should)match*here!/bu'cket")
    assert check is False


def test_generate_valid_s3_key_from_str_1_invalid():
    res = s3_utils.generate_valid_s3_key_from_str("s3-valid@key/nothing(should)match*here!/bu'cket")
    assert res == "s3-valid_key/nothing(should)match*here!/bu'cket"


def test_generate_valid_s3_key_from_str_4_invalid():
    res = s3_utils.generate_valid_s3_key_from_str("s3-valid@key/nothing&(should)match#here</bu'cket")
    assert res == "s3-valid_key/nothing_(should)match_here_/bu'cket"


def test_split_s3_path_easy():
    bucket = "bucket"
    key_prefix = "key_prefix"
    file_name = "file_name"
    res = s3_utils.split_s3_path(f'{bucket}/{key_prefix}/{file_name}')
    assert res == (bucket, f'{key_prefix}/', file_name)


def test_split_s3_path_nokey():
    bucket = "bucket"
    key_prefix = ""
    file_name = "file_name"
    res = s3_utils.split_s3_path(f'{bucket}/{key_prefix}/{file_name}')
    assert res == (bucket, "", file_name)


def test_split_s3_path_nofilename():
    bucket = "bucket"
    key_prefix = ""
    file_name = ""
    res = s3_utils.split_s3_path(f'{bucket}/{key_prefix}/{file_name}')
    assert res == (bucket, f'{key_prefix}', file_name)


def test_split_s3_path_hard():
    bucket = "bucket"
    key_prefix = "/key//prefix/with/error/"
    file_name = "/file_name/"
    res = s3_utils.split_s3_path(f'{bucket}/{key_prefix}/{file_name}')
    assert res == (bucket, "key/prefix/with/error/", "file_name")


def test_get_s3_formatted_bucket_path_double_slash():
    res = s3_utils.get_s3_formatted_bucket_path("my-bucket/", "/sub/bucket//directory/with/typo")
    assert res == ("my-bucket/sub/bucket/directory/with/typo/", "my-bucket", "sub/bucket/directory/with/typo/")


def test_get_s3_formatted_bucket_path_double_nokey_nofilename():
    res = s3_utils.get_s3_formatted_bucket_path("my-bucket/", "")
    assert res == ("my-bucket/", "my-bucket", "")


def test_get_s3_formatted_bucket_path_double_key_and_filename():
    res = s3_utils.get_s3_formatted_bucket_path("my-bucket", "key_prefix/", "file.jpg")
    assert res == ("my-bucket/key_prefix/file.jpg", "my-bucket", "key_prefix/file.jpg")


def test_get_s3_formatted_bucket_path_double_nokey_with_filename():
    res = s3_utils.get_s3_formatted_bucket_path("my-bucket", "", "key_prefix/file.jpg")
    assert res == ("my-bucket/key_prefix/file.jpg", "my-bucket", "key_prefix/file.jpg")


def test_generate_key_prefix_ok():
    date_str = datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")
    date = datetime.now()
    event_name = "event_test"
    d_label = {1: {"event": event_name, "img_id": 1, "timestamp": date_str},
               2: {"event": event_name, "img_id": 2, "timestamp": date_str}}
    key = upload.generate_key_prefix(d_label)
    assert key == f'{event_name}/{date.strftime("%Y%m%d")}/'


def test_generate_key_prefix_invalid_name():
    event_name = "event test"
    d_label = {1: {"event": event_name, "img_id": 1}, 2: {"event": event_name, "img_id": 2}}
    key = upload.generate_key_prefix(d_label)
    assert key is None


def test_generate_key_prefix_different_name():
    event_name = "event_test"
    d_label = {1: {"event": event_name, "img_id": 1}, 2: {"event": event_name, "img_id": 2}}
    key = upload.generate_key_prefix(d_label)
    assert key is None


def test_delete_all_bucket_refused():
    assert not s3_utils.delete_all_in_s3_folder("test", "", ["test"])
    assert not s3_utils.delete_all_in_s3_folder("test", None, ["test"])

