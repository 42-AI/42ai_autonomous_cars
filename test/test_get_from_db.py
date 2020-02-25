import pytest

from get_data.src import get_from_db


@pytest.fixture()
def list_of_existing_pic():
    return {
        "1517255696": {"img_id": "20200204T15-23-19-881268", "file_name": "20200204T15-23-19-881268.jpg",
                       "s3_bucket": "s3bucket/key/"},
        "1517255705": {"img_id": "20200204T15-23-08-574348", "file_name": "20200204T15-23-08-574348.jpg",
                       "s3_bucket": "s3bucket/key/"},
        "1537441219": {"img_id": "20200204T15-23-08-695024", "file_name": "20200204T15-23-08-695024.jpg",
                       "s3_bucket": "s3bucket/key/"}
    }


@pytest.fixture()
def list_of_missing_pic():
    return {
        "missing_pic_1": {"img_id": "missing_pic_1", "file_name": "missing_pic_1.jpeg", "s3_bucket": "s3bucket/key/"},
        "missing_pic_2": {"img_id": "missing_pic_2", "file_name": "missing_pic_2.jpeg", "s3_bucket": "s3bucket/key/"}
    }


def test_get_missing_picture_simple(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "test/resources"
    l_missing_pic = list_of_missing_pic
    l_wanted_pic = dict(**list_of_existing_pic, **l_missing_pic)
    assert get_from_db._get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic


def test_get_missing_picture_no_missing(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "test/resources"
    l_missing_pic = {}
    l_wanted_pic = dict(**list_of_existing_pic, **l_missing_pic)
    assert get_from_db._get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic


def test_get_missing_picture_only_missing(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "test/resources"
    l_missing_pic = list_of_missing_pic
    l_wanted_pic = dict(**list_of_existing_pic, **l_missing_pic)
    assert get_from_db._get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic


def test_get_missing_picture_empty(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "test/resources"
    l_missing_pic = {}
    l_wanted_pic = {}
    assert get_from_db._get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic


def test_get_missing_picture_not_a_dir(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "README.md"
    l_missing_pic = {}
    l_wanted_pic = {}
    assert get_from_db._get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic
