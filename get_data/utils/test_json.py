import argparse
import json
import matplotlib.pyplot as plt
import pathlib


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("labels_path", type=str,
                        help="Provide the relabeled json path.\n")
    return parser.parse_args()

def get_json_as_dic(labels_json):
    with open(labels_json) as data:
        json_dic = json.load(data)
    return json_dic

def get_issues(json_dic):
    wrong_creator = []
    wrong_img_id = []
    label_directions_all = []
    label_speeds_all = []
    key_to_delete = []
    delete = []

    for k, v in json_dic.items():
        img_id = v['img_id']
        created_by = v['label']['created_by']
        label_dir = v['label']['label_direction']
        label_speed = v['label']['label_speed']
        if k != img_id:
            wrong_img_id.append(img_id)
            key_to_delete.append(k)
        if created_by == 'auto':
            wrong_creator.append(created_by)
            key_to_delete.append(k)
        if 'to_delete' in v.keys():
            delete.append(k)
        label_directions_all.append(label_dir)
        label_speeds_all.append(label_speed)
    return key_to_delete, wrong_creator, wrong_img_id, label_directions_all, label_speeds_all, delete

def plot_labels_distribution(label_directions_all, label_speeds_all):
    label_directions_all = [0 if x=='A' else int(x) for x in label_directions_all]
    label_speeds_all = [0 if x=='A' else int(x) for x in label_speeds_all]
    fig = plt.figure()
    ax = fig.add_subplot(1, 2, 1)
    ax.hist(label_directions_all)
    ax = fig.add_subplot(1, 2, 2)
    ax.hist(label_speeds_all)
    plt.show()

# def create_cleaned_json():


if __name__ == '__main__':
    options = get_args()
    labels_json = pathlib.Path(options.labels_path)
    json_dic = get_json_as_dic(labels_json)
    key_to_delete, wrong_creator, wrong_img_id, label_directions_all, label_speeds_all, delete = get_issues(json_dic)

    print(f"""\tNb of created_by = auto: {len(wrong_creator)}
    nb of wrong image ids: {len(wrong_img_id)} 
    nb of directions_labels: {len(label_directions_all)}
    nb of speeds labels: {len(label_speeds_all)}
    nb of delete {len(delete)}""")

    # print(wrong_creator)
    # print(label_directions_all)
    plot_labels_distribution(label_directions_all, label_speeds_all)