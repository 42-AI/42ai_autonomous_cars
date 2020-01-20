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
