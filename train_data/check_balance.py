# Check balance.ipynb

#%%

from os import listdir
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import pandas as pd
%matplotlib inline
import matplotlib.pyplot as plt
import random

def load_photos(directory):
    images = []
    labels_speed = []
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
        value_speed = int(name.split('_')[0])
        value_dir = int(name.split('_')[1])
        labels_speed.append(value_speed)
        labels_dir.append(value_dir)
        images.append(image)
    return images, labels_speed, labels_dir

dataset = "../../Pics/test_noFE_mirrored"

# load images from both train and test groups
directory = '../../' + dataset
images, labels_speed, labels_dir = load_photos(directory)
nb_images = len(images)
print('Loaded Images and labels: %d' % nb_images)



#%%

l0 = [elem for elem in labels_dir if elem == 0]
l1 = [elem for elem in labels_dir if elem == 1]
l2 = [elem for elem in labels_dir if elem == 2]
l3 = [elem for elem in labels_dir if elem == 3]
l4 = [elem for elem in labels_dir if elem == 4]

#%%

len(l0), len(l1), len(l2), len(l3), len(l4)

#%%


