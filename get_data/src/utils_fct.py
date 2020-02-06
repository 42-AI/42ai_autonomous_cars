from datetime import datetime
from pathlib import Path
import json


def get_label_file_name(label_file_name):
    """Generate a unique label file name based on now timestamp."""
    return label_file_name.parent / f'{label_file_name.stem}_{datetime.now().strftime("%Y%m%dT%H-%M-%f")}.json'


def get_label_dict_from_file(file):
    """Open and read file containing the label(s). Return a dictionary of label or None on errors."""
    if not Path(file).is_file():
        print(f'File "{file}" can\'t be found.')
        return None
    with Path(file).open(mode='r', encoding='utf-8') as fp:
        d_label = json.load(fp)
    return d_label


def edit_label(d_label, field, value):
    """Set one field of all labels in d_label to a value."""
    for img_id, label in d_label.items():
        label[field] = value
