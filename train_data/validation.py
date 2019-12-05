# Validation_3.ipynb


# %%

from os import listdir
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import pandas as pd
% matplotlib
inline
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import random

import keras.backend as K
from keras.models import load_model


# %%

def load_photos(directory):
    images = []
    labels_dir = []
    dir_list = listdir(directory)
    random.shuffle(dir_list)
    for name in dir_list:
        filename = directory + '/' + name
        # load an image from file
        image = load_img(filename, target_size=(96, 160))
        # convert the image pixels to a numpy array
        image = img_to_array(image)
        # get image id + labels
        value_dir = float(name.split('_')[0])
        labels_dir.append(value_dir)
        images.append(image)
    return images, labels_dir


# %%

dataset = "../../../../Big_Race"

directory = dataset + '/Val'
images_val, labels_dir_val = load_photos(directory)
nb_images_val = len(images_val)
print('Loaded Images and labels for validation: %d' % nb_images_val)

images_val = np.array(images_val)
images_val /= 255.0

# %%

model_name = "model_race.h5"
model = load_model(model_name)

# %%

# print(model.to_json())

# %%

# Get predictions
all_preds = model.predict(images_val)

dir_preds = []
for elem in all_preds:
    dir_preds.append(np.argmax(elem))

# %%

dir_preds

# %%

res = 0

i_0 = 1
res_0 = 0
res_0_1 = 0
res_0_2 = 0

i_1 = 1
res_1 = 0
res_1_0 = 0
res_1_2 = 0

i_2 = 1
res_2 = 0
res_2_0 = 0
res_2_1 = 0

for value in labels_dir_val:
    if value == 0:
        i_0 += 1
    elif value == 1:
        i_1 += 1
    elif value == 2:
        i_2 += 1

for i, value in enumerate(dir_preds):
    if value != labels_dir_val[i]:
        res += 1
        if labels_dir_val[i] == 0:
            res_0 += 1
            if value == 1:
                res_0_1 += 1
            elif value == 2:
                res_0_2 += 2
        elif labels_dir_val[i] == 1:
            res_1 += 1
            if value == 0:
                res_1_0 += 1
            elif value == 2:
                res_1_2 += 1
        elif labels_dir_val[i] == 2:
            res_2 += 1
            if value == 0:
                res_2_0 += 1
            elif value == 1:
                res_2_1 += 1

print("total error = " + str(res / i), "0_error = " + str(res_0 / i_0), "1_error = " + str(res_1 / i_1),
      "2_error = " + str(res_2 / i_2))

# %%

x = ['0', '1', '2']
plt.bar(x, height=[res_0 / i_0, res_1 / i_1, res_2 / i_2])
plt.xticks(x, ['0', '1', '2']);
plt.title("Mean Errors by direction")

# %%

x = ['1', '2']
plt.bar(x, height=[res_0_1 / i_0, res_0_2 / i_0])
plt.xticks(x, ['1', '2']);
plt.title("0 Errors")

# %%

x = ['0', '2']
plt.bar(x, height=[res_1_0 / i_1, res_1_2 / i_1])
plt.xticks(x, ['0', '2']);
plt.title("1 Errors")

# %%

x = ['0', '1']
plt.bar(x, height=[res_2_0 / i_2, res_2_1 / i_2])
plt.xticks(x, ['0', '1']);
plt.title("2 Errors")

# %%


# %%


# %%


# %%


