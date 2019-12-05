#  Patate/Data_processing/Training/3_directions_models_Opti_speed.ipynb

import os
import random
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt

import keras.callbacks
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import Model
from keras.layers import *

import model_params_setter


class TrainModel:
    def __init__(self, images_dir, model_params):
        self.images_dir = images_dir
        self.model_name = model_params['name']
        self.model_inputs = model_params['inputs']
        self.model_outputs = model_params['outputs']
        self.model = None

    def load_images(self, show_test=True):
        images, labels_speed, labels_directions = [], [], []
        for filename in random.shuffle(os.listdir(self.images_dir)):
            filepath = self.images_dir + '/' + filename
            # load an image from file
            image = load_img(filepath, target_size=(96, 160))
            # convert the image pixels to a numpy array
            image = img_to_array(image)
            # get image id + labels
            value_dir = float(filename.split('_')[1])
            value_speed = float(filename.split('_')[0])
            labels_directions.append(value_dir)
            labels_speed.append(value_speed)
            images.append(image)
            labels_directions = np.array(pd.get_dummies(labels_directions))
            labels_speed = np.array(pd.get_dummies(labels_speed))
        images = self.normalize_images(images)
        if show_test:
            print('Loaded Images and labels for training: {}'.format(len(images)))
            print("For the image below, direction label is: {} and speed label is {}".format(labels_directions[42],
                                                                                             labels_speed[42]))
            plt.imshow(images[42])
        return images, labels_speed, labels_directions

    @staticmethod
    def normalize_images(images):
        return np.array(images) / 255.0

    def train(self):
        images, labels_speed, labels_directions = self.load_images()
        self.model = Model(inputs=self.model_inputs, outputs=self.model_outputs)
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(self.model.summary)
        best_checkpoint = keras.callbacks.ModelCheckpoint(self.model_name, monitor='val_loss', verbose=1,
                                                          save_best_only=True, mode='min')
        self.model.fit(images, [labels_speed, labels_directions], batch_size=64, epochs=100, validation_split=0.2,
                       verbose=1, callbacks=[best_checkpoint])

    def graph(self):
        history_df = pd.DataFrame(self.model.history, index=self.model.epoch)
        history_df.plot(ylim=(0, 1))


if __name__ == '__main__':
    images_directory, model_parameters = model_params_setter.get_params()
    train_model = TrainModel(images_directory, model_parameters)
    train_model.train()
    train_model.graph()
