from datetime import datetime
from pathlib import Path
import json
import hashlib

from get_data.src import s3_utils


def get_label_file_name(directory, base_name="labels", suffix=".json"):
    """Generate a unique label file name based on now timestamp."""
    # return Path(label_file).parent / f'{label_file.stem}_{datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")}{label_file.suffix}'
    return Path(directory) / f'{base_name}_{datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")}{suffix}'


def get_label_dict_from_file(file):
    """Open and read file containing the label(s). Return a dictionary of label or None on errors."""
    if not Path(file).is_file():
        print(f'File "{file}" can\'t be found.')
        return None
    with Path(file).open(mode='r', encoding='utf-8') as fp:
        d_label = json.load(fp)
    return d_label


def remove_label_to_delete_from_dict(d_label):
    """
    Removed label in a dictionary of labels that have a "to_delete" field set to True. Label are removed from the
    dictionary in place.
    :param d_label:     [dict]          Dictionary of labels where the key is the img_id the label points to and the
                                        value is the label itself:
                                        {
                                          "20200115T15-45-55-123456": {...},
                                          ...
                                        }
    :return:            [list of dict]  List of item removed from the input dictionary:
                                        [{"img_id": "xxx", "s3_key": "xxx", "label_fingerprint": "xxx"}, {...}, ...]
    """
    l_removed_item = []
    for img_id in list(d_label.keys()):
        label = d_label[img_id]
        try:
            to_delete = label["to_delete"]
            if not to_delete:
                label.pop("to_delete")
        except KeyError:
            to_delete = False
        if to_delete:
            d_label.pop(img_id)
            _, _, s3_key = s3_utils.get_s3_formatted_bucket_path(label["s3_bucket"], "", label["img_id"])
            l_removed_item.append({"img_id": img_id, "s3_key": s3_key, "label_fingerprint": label["label_fingerprint"]})
    return l_removed_item


def edit_label(d_label, field, value, filter_out=None):
    """
    Set one field of all labels in d_label to a value.
    :param d_label:         [dict]      Label dictionary to edit
    :param field:           [string]    Name of the field to edit
    :param value:           [object]    Value to put in the field
    :param filter_out:      [list]      list of img_id not to be affected by the edit
    """
    filter_out = [] if filter_out is None else filter_out
    for img_id, label in d_label.items():
        if img_id not in filter_out:
            label[field] = value


def get_label_finger_print(label):
    id_str = str(label["img_id"]) + \
             str(label["label"]["created_by"]) + \
             str(label["label"]["label_direction"]) + \
             str(label["label"]["label_speed"]) + \
             str(label["label"]["nb_of_direction"]) + \
             str(label["label"]["nb_of_speed"])
    return hashlib.md5(id_str.encode('utf-8')).hexdigest()
