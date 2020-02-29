"""
Aim
Put all the images and the jsons in the folder
Script will
- merge jsons
- remove all keys where created by is auto
"""

import argparse
import json
import pathlib

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path", type=str,
                        help="Provide the folder path.\n")
    return parser.parse_args()

def get_dic_from_json(json_file):
    with open(json_file) as data:
        return json.load(data)

def merge_jsons(directory):
    json_lists = list(pathlib.Path(directory).glob('*.json'))
    labels_dict = {}
    for label_json in json_lists:
        labels_dict.update(get_dic_from_json(label_json))
    return labels_dict

def clean_global_dict(labels_dic):
    key_to_delete = []
    for k, v in labels_dic.items():
        if v['label']['created_by'] == 'auto':
            key_to_delete.append(k)
    print(len(key_to_delete))
    for k in key_to_delete:
        item = labels_dic.pop(k, None)
        # print(item)
    return labels_dic

def create_cleaned_json(directory, clean_dict):
    json_path = f"{directory}/cleaned_json.json"
    with open(json_path, 'w', encoding='utf-8') as fd:
        json.dump(clean_dict, fd, indent=4)

if __name__ == '__main__':
    options = get_args()
    directory = options.folder_path
    labels_dict = merge_jsons(directory)
    print(len(labels_dict))
    labels_dict = clean_global_dict(labels_dict)
    print(len(labels_dict))
    create_cleaned_json(directory, labels_dict)