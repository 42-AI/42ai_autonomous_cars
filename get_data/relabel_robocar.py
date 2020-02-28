import sys
import os
import json
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

from get_data.src import label_handler, utils_fct

speed_dic = {
    0: 316,
    1: 311
}

direction_dic = {
    0: 250,
    1: 290,
    2: 327,
    3: 364,
    4: 400
}

def get_normalized_speed(speed_idx):
    x = (speed_dic[speed_idx] - 307) / (322 - 307)
    return (1 - x)

def get_normalized_direction(dir_idx):
    return (direction_dic[dir_idx] - 326) / 325

def get_speed_index(speed):
    if speed > 0.8:
        return 1
    return 0

def get_direction_index(direction):
    if direction < -0.8:
        return 0
    elif -0.8 <= direction <= -0.1:
        return 1
    elif -0.1 <= direction <= 0.1:
        return 2
    elif 0.1 <= direction <= 0.8:
        return 3
    elif direction > 0.8:
        return 4

def relabel(directory):
    json_data = dict()
    for i, filename in enumerate(os.listdir(directory)):
        if filename.endswith(".jpg"):
            new_filename = "20191130T12-00-00-{:06d}".format(i)
            filename_list = filename.rsplit('/', 1)
            speed, direction, name = filename_list[0].split('_', 2)
            # clean_new_filename = new_filename[0].rsplit('.', 1)[0]
            #print(os.path.join(directory, a[0]))
            speed_idx = get_speed_index(float(speed))
            dir_idx = get_direction_index(float(direction))
            #print(speed, direction, name, new_filename, clean_new_filename, speed_idx, dir_idx)
            json_data.update(create_json_label(speed, direction, new_filename, speed_idx, dir_idx))
            os.rename(f"{directory}/{filename}", f"{directory}/{new_filename}.jpg")
        else:
            continue
    with open(f'{directory}/robocar3011.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

def create_json_label(speed, direction, name, speed_idx, dir_idx):

    label_template = {
        name: {
            "s3_bucket": "",
            "car_setting": {
                "camera": {
                    "resolution-horizontal": 160,
                    "resolution-vertical": 96,
                    "frame_rate": 32,
                    "exposure_mode": "auto",
                    "camera_position": 120
                },
            "constant": {
                "max_speed": 307,
                "stop_speed": 322,
                "max_direction_l": 1,
                "max_direction_r": 651,
                "joystick_to_raw_dir_mapping": [],
                "trigger_to_raw_speed_mapping": [],
                "label_to_raw_dir_mapping": [
                    250,
                    290,
                    327,
                    364,
                    400
                ],
                "label_to_raw_speed_mapping": [
                    316,
                    311
                ],
                "head_up": 150,
                "head_down": 120
            }
            },
            "hardware_conf": {
                "car": "patate",
                "version": 1,
                "computer": "Raspberry_Pi2",
                "camera": "Picam"
            },
            "event": "robocar",
            "track": "",
            "track_picture": "",
            "track_type": "single lane",
            "dataset": [
                {
                    "name": "old_pics_2019",
                    "comment": "pictures take in 2019",
                    "query": None
                }
            ],
            "comment": "",
            "upload_date": "",
            "img_id": name,
            "file_name": name + ".jpg",
            "file_type": "jpg",
            "raw_value": {
                "raw_direction": direction_dic[dir_idx],
                "raw_speed": speed_dic[speed_idx],
                "normalized_speed": get_normalized_speed(speed_idx),
                "normalized_direction": get_normalized_direction(dir_idx)
            },
            "label": {
                "label_direction": dir_idx,
                "label_speed": speed_idx,
                "created_by": "auto",
                "created_on_date": name,
                "raw_dir_to_label_mapping": [
                    250,
                    290,
                    327,
                    364,
                    400
                ],
                "raw_speed_to_label_mapping": [
                    316,
                    311
                ],
                "nb_of_direction": 5,
                "nb_of_speed": 2
            },
            "timestamp": name,
            "label_fingerprint": '',
            "raw_picture": True
        }
    }
    label_template[name]['label_fingerprint'] = utils_fct.get_label_finger_print(label_template[name])
    return label_template


if __name__ == "__main__":
    directory = "/Users/Pablo/Downloads/robocar"
    relabel(directory)