import pytest

from get_data import get_from_db


@pytest.fixture()
def list_of_existing_pic():
    return [
        {"img_id": "1517255696", "file_name": "0_0_1517255696.923487.jpg", "location": "s3bucket/key/"},
        {"img_id": "1517255705", "file_name": "0_2_1517255705.4247274.jpg", "location": "s3bucket/key/"},
        {"img_id": "1537441219", "file_name": "0_3_1537441219.79.jpg", "location": "s3bucket/key/"}
    ]


@pytest.fixture()
def list_of_missing_pic():
    return [
        {"img_id": "missing_pic_1", "file_name": "missing_pic_1.jpeg", "location": "s3bucket/key/"},
        {"img_id": "missing_pic_2", "file_name": "missing_pic_2.jpeg", "location": "s3bucket/key/"}
    ]


def test_get_missing_picture_simple(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "get_data/sample"
    l_missing_pic = list_of_missing_pic
    l_wanted_pic = list_of_existing_pic + l_missing_pic
    assert get_from_db.get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic


def test_get_missing_picture_no_missing(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "get_data/sample"
    l_missing_pic = []
    l_wanted_pic = list_of_existing_pic + l_missing_pic
    assert get_from_db.get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic


def test_get_missing_picture_only_missing(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "get_data/sample"
    l_missing_pic = list_of_missing_pic
    l_wanted_pic = [] + l_missing_pic
    assert get_from_db.get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic


def test_get_missing_picture_empty(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "get_data/sample"
    l_missing_pic = []
    l_wanted_pic = []
    assert get_from_db.get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic


def test_get_missing_picture_not_a_dir(list_of_missing_pic, list_of_existing_pic):
    pic_dir = "README.md"
    l_missing_pic = []
    l_wanted_pic = []
    assert get_from_db.get_missing_picture(pic_dir, l_wanted_pic) == l_missing_pic
