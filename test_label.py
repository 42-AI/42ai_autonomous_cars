import pytest
import json

from get_data.utils import label_handler as lb


def test_init_label_file_valid_dir():
    output = "get_data/sample"
    label = lb.Label(output_dir=output)
    session_template = label.get_session_template()
    assert session_template != {}
    assert label.output_dir == output
    assert label.template["location"] == output


def test_init_label_file_invalid_dir():
    output = "wrong/dir"
    with pytest.raises(IOError):
        label = lb.Label(output_dir=output)


def test_init_label_file_wrong_json_format():
    output = "get_data/sample/wrong_format"
    with pytest.raises(json.JSONDecodeError):
        label = lb.Label(output_dir=output)


def test_change_output_dir():
    output = "get_data/sample"
    label = lb.Label(output_dir=output)
    label.output_dir = "foo/bar/"
    assert label.template["location"] == "foo/bar/"
    assert label.output_dir == "foo/bar/"


def test_change_car_setting():
    output = "get_data/sample"
    label = lb.Label(output_dir=output)
    car_setting = {"setting1": 10, "s2": "boabab"}
    label.car_setting = car_setting
    assert label.template["car_setting"] == car_setting
    assert label.car_setting == car_setting


def test_change_session_template():
    output = "get_data/sample"
    label = lb.Label(output_dir=output)
    session_template = {"t1": 10, "t2": "boabab"}
    label.session_template = session_template
    for key, val in session_template.items():
        assert label.template[key] == val
        assert label.session_template[key] == val


def test_change_hardware_conf():
    output = "get_data/sample"
    label = lb.Label(output_dir=output)
    hardware = {"t1": 10, "t2": "boabab"}
    label.hardware_conf = hardware
    assert label.template["hardware"] == hardware
    assert label.hardware_conf == hardware


if __name__ == "__main__":
    test_init_label_file_valid_dir()
    test_init_label_file_invalid_dir()
    test_init_label_file_wrong_json_format()
    test_change_output_dir()
    test_change_car_setting()
    test_change_session_template()
    test_change_hardware_conf()
