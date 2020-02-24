import argparse
import datetime
import json
import pathlib
import random

import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

from train_data import model_params_setter_new_multi


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("labels_path", type=str,
                        help="Provide the model path.\n")
    return parser.parse_args()


class TrainModel:
    def __init__(self, labels_path, seed=42, validation_split=0.2, batch_size=32, nb_epochs=20, name='saved_model'):
        tf.random.set_seed(seed)
        random.seed(seed)
        self.images_json = None
        self.images_dir = None
        self.validation_split = validation_split
        self.nb_epochs = nb_epochs

        self.model = None
        self.name = name

        self._get_images_json(labels_path)
        self.images, self.directions, self.speeds = self._get_feat_labels_tensors()

    def _get_images_json(self, labels_path):
        labels_json = pathlib.Path(labels_path)
        self.images_dir = labels_json.parent

        with open(labels_json) as data:
            self.images_json = json.load(data)

        # est ce qu'il faudrait pas mieux shuffle et split la ?
        # TODO shuffle ici les images ac seed ?

    def _get_feat_labels_tensors(self):
        features, speeds, directions = [], [], []
        images_values = list((self.images_json).values())
        random.shuffle(images_values)
        for v in images_values:
            features.append(self._get_image(str(self.images_dir / v['file_name'])))
            speeds.append(v['label']['label_speed'])
            directions.append(v['label']['label_direction'])

        return np.asarray(features), np.asarray(directions), np.asarray(speeds)

    def _get_image(self, image_path):
        image_str = tf.io.read_file(image_path)
        image = tf.image.decode_jpeg(image_str, channels=3).numpy() / 255.0
        return image
    # def train preprocess ? tf.image brightness, saturation... or put it separately and create images ?

    def show_images(self, rows, cols):
        fig = plt.figure()
        for i, image in enumerate(self.images):
            if i == rows * cols:
                break
            ax = fig.add_subplot(rows, cols, i + 1)
            ax.imshow(image[:, :, :])
        plt.show()

    def train(self):
        self.model = model_params_setter_new_multi.get_model_params()
        self.model.build(input_shape=(None, 96, 160, 3))
        self.model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                      optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), metrics=['accuracy'])
        self.model.summary()


        best_checkpoint = tf.keras.callbacks.ModelCheckpoint(self.name, monitor='val_loss', verbose=0,
                                                             save_best_only=True, mode='min')
        log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

        self.history = self.model.fit(self.images, [self.directions, self.speeds], epochs=self.nb_epochs,
                                      validation_split=self.validation_split,
                                 shuffle=True, verbose=1, callbacks=[best_checkpoint, tensorboard_callback])

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

    # def _show_balance(self):
    #     labels_speed_df = pd.Series(self.labels_speed)
    #     print(labels_speed_df.value_counts(), labels_speed_df.describe())
    #     labels_directions_df = pd.Series(self.labels_directions)
    #     print(labels_directions_df.value_counts(), labels_directions_df.describe())
    #     # TODO (pclement): make graphs?
    # or use kibana ?


if __name__ == '__main__':
    options = get_args()
    train_model = TrainModel(options.labels_path)
    # train_model.show_images(5, 10)
    train_model.train()

    # train_model.predict()
