from get_data.utils import s3_utils


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
