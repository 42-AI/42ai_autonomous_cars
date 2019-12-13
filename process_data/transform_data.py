import argparse
import os

# noinspection PyUnresolvedReferences,PyUnresolvedReferences
from PIL import Image


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory_path", type=str,
                        help="Provide the directory path of the data you want to change path.\n")
    return parser.parse_args()


class TransformData:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    # TODO (pclement): For all, make it modular, define a target_directory where you copy renamed data (avoid loosing raw data)
    # TODO (pclement): Use a dictionnary with speed, direction head rather than list that makes code inconsistent
    #  + ideally just amend the database once images stored in S3

    def five_to_three(self):
        for filename in os.listdir(self.dir_path):
            filename_array = filename.split("_")
            if filename_array[1] == "1":
                os.rename(os.path.join(self.dir_path, filename),
                          os.path.join(self.dir_path, "{}_0_{}".format(filename_array[0], filename_array[2])))
            elif filename_array[1] == "2":
                os.rename(os.path.join(self.dir_path, filename),
                          os.path.join(self.dir_path, "{}_1_{}".format(filename_array[0], filename_array[2])))
            elif filename_array[1] in ["3", "4"]:
                os.rename(os.path.join(self.dir_path, filename),
                          os.path.join(self.dir_path, "{}_2_{}".format(filename_array[0], filename_array[2])))

    def reverse_n(self, n=3):
        # TODO (pclement) : why reverse 3 has elemtab ==2 and elm_tab ==3 ???
        for filename in os.listdir(self.dir_path):
            filename_array = filename.split("_")
            img = Image.open(os.path.join(self.dir_path, filename))
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            for i in range(n):
                if n == 3 and filename_array[0] == i:
                    updated_info = n - i - 1 % 10
                    img.save(os.path.join(self.dir_path,
                                          "{}_r{}".format(updated_info, filename_array[1])))
                    break
                elif n == 5 and filename_array[1] == i:
                    updated_info = n - i - 1 % 10
                    img.save(os.path.join(self.dir_path,
                                          "{}_{}_r{}".format(updated_info, filename_array[1], filename_array[2])))
                    break

    def black_and_white(self):
        for elem in os.listdir(self.dir_path):
            col = Image.open(os.path.join(self.dir_path, elem))
            transformed_image = col.convert('L')
            transformed_image.save(os.path.join(self.dir_path, elem))

    def truncate(self):
        for filename in os.listdir(self.dir_path):
            os.rename(os.path.join(self.dir_path, filename), os.path.join(self.dir_path, filename[2:]))

    def rename_float_tags(self):
        # TODO (pclement) no checks on name_array but we want to create a file separately. And use dictionnary to have clear names
        # TODO (pclement) make the thresholds modulars
        # TODO (pclement) WHY is the direction center so close to 0. could it be -0.1, 0.1?
        for filename in os.listdir(self.dir_path):
            filename_array = filename.split("_")
            speed = 0
            direction = 4
            if float(filename_array[0]) > 0.8:
                speed = 1
            if float(filename_array[1]) < -0.8:
                direction = 0
            elif float(filename_array[1]) < -0.001:
                direction = 1
            elif float(filename_array[1]) < 0.001:
                direction = 2
            elif float(filename_array[1]) < 0.8:
                direction = 3
            new_filename = "{}_{}_{}".format(speed, direction, filename_array[2])
            os.rename(os.path.join(self.dir_path, filename), os.path.join(self.dir_path, new_filename))


if __name__ == '__main__':
    options = get_args()
    TransformData(options.directory_path).five_to_three()
    TransformData(options.directory_path).reverse_n()
    TransformData(options.directory_path).black_and_white()
    TransformData(options.directory_path).rename_float_tags()
