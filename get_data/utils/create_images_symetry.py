"""
Aim
Put all the image and json in folder

get json
create other sym_folder
for each image in folder
create sym_image and put it in other folder

change json dir label 0/4 1/3

"""

import argparse
import datetime
import json
import pathlib
import tensorflow as tf

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path", type=str,
                        help="Provide the folder path.\n")
    return parser.parse_args()

def get_dic_from_json(directory):
    json_path = list(pathlib.Path(directory).glob('*.json'))
    with open(json_path[0]) as data:
        return json.load(data)


def create_sym_json(labels_dic, directory):
    sym_json_path_dir = pathlib.Path(directory).parent / f'sym_{directory}'
    sym_json_path_dir.mkdir(parents=True, exist_ok=True)
    sym_json_p = sym_json_path_dir / pathlib.Path("sym_json.json")

    return sym_json_p


# def merge_jsons(directory):

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

def import_images(sym_labels_dict, sym_json_path, directory):
    # sym_labels_dict = get_dic_from_json(sym_json_path.parent)
    renamed_sym_labels_dict = {}
    for k, v in sym_labels_dict.items():
        v['label']['label_direction'] = str(4 - int(v['label']['label_direction']))
        date = datetime.datetime.now()
        new_key = date.strftime("%Y%m%dT%H-%M-%S-%f")
        v['file_name'] = f"{new_key}.jpg"
        new_filepath = sym_json_path.parent / v['file_name']
        image_str = tf.io.read_file(str(f"{directory}/{k}.jpg"))
        image = tf.image.decode_jpeg(image_str, channels=3)
        sym_image = tf.image.flip_left_right(image)
        sym_image_encoded = tf.io.encode_jpeg(sym_image)
        tf.io.write_file(str(new_filepath), sym_image_encoded)
        v['raw_picture'] = "false"
        v['comment'] = "Vertical symetry: used tf.image.flip_left_right(image)"
        renamed_sym_labels_dict[new_key] = v
    #print(renamed_sym_labels_dict)
    #create_sym_json()
    with sym_json_path.open("w", encoding="utf-8") as fd:
        json.dump(renamed_sym_labels_dict, fd, indent=4)

if __name__ == '__main__':
    options = get_args()
    directory = options.folder_path
    labels_dict = get_dic_from_json(directory)
    print(len(labels_dict))
    sym_json_path = create_sym_json(labels_dict, directory)
    import_images(labels_dict, sym_json_path, directory)
    #labels_dict = clean_global_dict(labels_dict)
    #print(len(labels_dict))
    #create_cleaned_json(directory, labels_dict)