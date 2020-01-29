import pytest
import json
from pathlib import Path

from get_data.src import label_handler as lb
from conf.path import SESSION_TEMPLATE_NAME


def test_label_handler_empty_init():
    label = lb.Label()
    assert label is not None


def test_label_handler_change_output_dir():
    label = lb.Label()
    label.picture_dir = "foo/bar/"
    assert label[label.picture_dir_key] == "foo/bar/"
    assert label.picture_dir == "foo/bar/"


def test_label_handler_change_output_dir_bis():
    label = lb.Label()
    label[label.picture_dir_key] = "foo/bar/"
    assert label[label.picture_dir_key] == "foo/bar/"
    assert label.picture_dir == "foo/bar/"


def test_label_handler_init_file_valid_dir():
    output = "test/resources"
    session_template_file = Path(output) / SESSION_TEMPLATE_NAME
    label = lb.Label(picture_dir=output)
    with session_template_file.open(mode='r', encoding='utf-8') as fp:
        session_template = json.load(fp)
    assert label.picture_dir == output
    assert label[label.picture_dir_key] == output
    for key, val in session_template.items():
        assert label[key] == val


def test_label_handler_init_invalid_dir():
    output = "wrong/dir"
    with pytest.raises(IOError):
        label = lb.Label(picture_dir=output)


def test_label_handler_init_wrong_json_format():
    output = "test/resources/wrong_format"
    with pytest.raises(json.JSONDecodeError):
        label = lb.Label(picture_dir=output)


def test_label_handler_set_label():
    output = "test/resources"
    label = lb.Label(picture_dir=output)
    pic_val = {"img_id": 42, "file_name": "test.jpg", "timestamp": 123456789}
    raw_val = {"raw_speed": 10, "raw_direction": 20}
    label_val = {"speed": 100, "direction": 200}
    label.set_label(**pic_val, **label_val, **raw_val)
    for key, val in pic_val.items():
        assert label[key] == val
        assert label["file_type"] == "jpg"
    for key, val in raw_val.items():
        assert label["raw_value"][key] == val
    for key, val in label_val.items():
        assert label["label"][0][key] == val
    assert label["label"][0]["created_by"] == "auto"


def test_label_handler_get_copy():
    output = "test/resources"
    label = lb.Label(picture_dir=output)
    l_label = []
    for i in range(10):
        pic_val = {"img_id": i, "file_name": f'file_{i}.png', "timestamp": i / 10}
        raw_val = {"raw_speed": i+10, "raw_direction": i+20}
        label_val = {"speed": i+100, "direction": i+200}
        label.set_label(**pic_val, **label_val, **raw_val)
        l_label.append(label.get_copy())
    for i, item in enumerate(l_label):
        pic_val = {"img_id": i, "file_name": f'file_{i}.png', "timestamp": i / 10}
        raw_val = {"raw_speed": i+10, "raw_direction": i+20}
        label_val = {"speed": i+100, "direction": i+200}
        for key, val in pic_val.items():
            assert item[key] == val
            assert item["file_type"] == "png"
        for key, val in raw_val.items():
            assert item["raw_value"][key] == val
        for key, val in label_val.items():
            assert item["label"][0][key] == val


if __name__ == "__main__":
    test_label_handler_empty_init()
