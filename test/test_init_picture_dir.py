from io import StringIO
from pathlib import Path
import pytest
import json

from get_data.src import init_picture_folder as init
from conf.path import SESSION_TEMPLATE_NAME


@pytest.fixture
def init_test(monkeypatch):
    monkeypatch.setattr('sys.stdin', StringIO("\n"))
    output = Path("test/test_tmp_dir")
    session_template = {
        "event": "unittest",
        "comment": "just for test"
    }
    session_file = output / SESSION_TEMPLATE_NAME
    yield output, session_file, session_template


def test_init_picture_folder_mkdir(init_test):
    output, session_file, session_template = init_test
    init.init_picture_folder(output)
    assert output.is_dir() is True
    assert session_file.is_file() is True
    session_file.unlink()
    output.rmdir()


def test_init_picture_folder_existok(init_test):
    output, session_file, session_template = init_test
    output.mkdir()
    init.init_picture_folder(output)
    assert output.is_dir() is True
    assert session_file.is_file() is True
    session_file.unlink()
    output.rmdir()


def test_init_picture_folder_file_exist(init_test):
    output, session_file, session_template = init_test
    output.mkdir()
    with session_file.open(mode='w', encoding='utf-8') as fp:
        json.dump(session_template, fp)
    init.init_picture_folder(output)
    with session_file.open(mode='r', encoding='utf-8') as fp:
        created_template = json.load(fp)
    assert created_template == session_template
    session_file.unlink()
    output.rmdir()
