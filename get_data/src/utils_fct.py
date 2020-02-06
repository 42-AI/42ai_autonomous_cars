from datetime import datetime
from pathlib import Path
import json
import hashlib


def get_label_file_name(label_file):
    """Generate a unique label file name based on now timestamp."""
    return Path(label_file).parent / f'{label_file.stem}_{datetime.now().strftime("%Y%m%dT%H-%M-%f")}{label_file.suffix}'


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


def get_label_finger_print(label):
    id_str = str(label["img_id"]) + \
             str(label["label"]["created_by"]) + \
             str(label["label"]["label_direction"]) + \
             str(label["label"]["label_speed"]) + \
             str(label["label"]["nb_of_direction"]) + \
             str(label["label"]["nb_of_speed"])
    return hashlib.md5(id_str.encode('utf-8')).hexdigest()
