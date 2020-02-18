import json
import argparse
from pathlib import Path
import re

import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

from get_data.src import utils_fct


def substitute_in_dictionary(dictionary, match_regex, substitute, field_list, count=0, deep=False):
    if deep is True:
        print("Not yet implemented")
    count = count
    for field, value in dictionary.items():
        if field in field_list and isinstance(value, str):
            dictionary[field], nb = match_regex.subn(substitute, value)
            count += nb
    return count


def substitute_matching_char():
    """ Substitute matching char in a json with a specified char. """
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Path to the json file to be modified")
    parser.add_argument("-m", "--match", type=str, help="Char that shall be substituted", required=True)
    parser.add_argument("-s", "--substitute",
                        required=True,
                        help="Char to substitute in place of the matching chars. Shall be of length 1.")
    parser.add_argument("-f", "--field",
                        type=str,
                        nargs="+",
                        required=True,
                        help="List of field where the substitution should happen")
    args = parser.parse_args()
    field_list = args.field
    regex = re.compile(r'[args.match]')
    with Path(args.file).open(mode='r', encoding='utf-8') as fp:
        l_label = json.load(fp)
    if not isinstance(l_label, list):
        l_label = [l_label]
    count = 0
    for label in l_label:
        count += substitute_in_dictionary(label, regex, args.substitute, field_list, deep=False)
    print(f'{count} substitution made')
    with Path(args.file).open(mode='w', encoding='utf-8') as fp:
        json.dump(l_label, fp, indent=4)


def custom_change_field():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Path to the json file to be modified")
    args = parser.parse_args()
    with Path(args.file).open(mode='r', encoding='utf-8') as fp:
        d_label = json.load(fp)
    for img_id, label in d_label.items():
        # label["label_fingerprint"] = utils_fct.get_label_finger_print(label)
        label["location"] = "../Pics/NewPull"
    with Path(args.file).open(mode='w', encoding='utf-8') as fp:
        json.dump(d_label, fp, indent=4)


if __name__ == "__main__":
    # substitute_matching_char()
    custom_change_field()
    pass
