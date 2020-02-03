from io import StringIO
from pathlib import Path

from get_data.src import init_picture_folder as init


def test_init_picture_folder(monkeypatch):
    monkeypatch.setattr('sys.stdin', StringIO("\n"))
    output = "test/tmp_folder"
    init.init_picture_folder(output)
    assert Path(output).is_dir() == True
