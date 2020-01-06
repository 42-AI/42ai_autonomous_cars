#  Patate/Data_processing/Training/3_directions_models_Opti_speed.ipynb
# show_balance replaces check balance.ipynb

import numpy as np
import os
import random

import matplotlib.pyplot as plt
import pandas as pd

import tensorflow.keras.callbacks
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array

import model_params_setter
from utils.path import TRAINING_IMAGES_DIRECTORY, VALIDATION_IMAGES_DIRECTORY


class TrainModel:
    def __init__(self, model_params):
        self.images_dir = None
        self.images = None
        self.labels_directions = None
        self.labels_speed = None
        self.model_name = model_params['name']
        self.model_inputs = model_params['inputs']
        self.model_outputs = model_params['outputs']
        self.model = None

    @staticmethod
    def _normalize_images(images):
        return np.array(images) / 255.0

    def _show_balance(self):
        labels_speed_df = pd.Series(self.labels_speed)
        print(labels_speed_df.value_counts(), labels_speed_df.describe())
        labels_directions_df = pd.Series(self.labels_directions)
        print(labels_directions_df.value_counts(), labels_directions_df.describe())
        # TODO (pclement): make graphs?

    def load_images(self, images_dir, show_test=True, show_balance=False):
        images, labels_speed, labels_directions = [], [], []
        self.images_dir = images_dir
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
            self.labels_directions = np.array(pd.get_dummies(labels_directions))
            self.labels_speed = np.array(pd.get_dummies(labels_speed))
        self.images = self._normalize_images(images)
        if show_test is True:
            print('Loaded Images and labels for training: {}'.format(len(self.images)))
            print("For the image below, direction label is: {} and speed label is {}".format(self.labels_directions[42],
                                                                                             self.labels_speed[42]))
            plt.imshow(self.images[42])
        if show_balance is True:
            self._show_balance()

    def train(self):
        self.model = Model(inputs=self.model_inputs, outputs=self.model_outputs)
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(self.model.summary)
        best_checkpoint = tensorflow.keras.callbacks.ModelCheckpoint(self.model_name, monitor='val_loss', verbose=1,
                                                          save_best_only=True, mode='min')
        self.model.fit(self.images, [self.labels_speed, self.labels_directions],
                       batch_size=64, epochs=100, validation_split=0.2,
                       verbose=1, callbacks=[best_checkpoint])
        # TODO (pclement): use tensorboard

    def training_graph(self):
        history_df = pd.DataFrame(self.model.history, index=self.model.epoch)
        history_df.plot(ylim=(0, 1))

    def predict(self):
        # TODO (pclement): split training/prediciton images? to get list of images used to train (see how db works.)
        predictions = self.model.predict(self.images)
        speed_preds = []
        for elem in predictions[0]:
            speed_preds.append(np.argmax(elem))
        dir_preds = []
        for elem in predictions[1]:
            dir_preds.append(np.argmax(elem))
        # TODO (pclement): use vecorized numpy method to define those
        return predictions, np.array(speed_preds), np.array(dir_preds)


if __name__ == '__main__':
    model_parameters = model_params_setter.get_model_params()
    train_model = TrainModel(model_parameters)
    train_model.load_images(TRAINING_IMAGES_DIRECTORY, show_test=True, show_balance=True)
    train_model.train()
    train_model.training_graph()
    train_model.load_images(VALIDATION_IMAGES_DIRECTORY, show_test=True, show_balance=False)
    train_model.predict()
