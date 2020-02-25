import argparse
import datetime
import json
import pathlib
import random
import shutil

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

import model_setter


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("labels_path", type=str,
                        help="Provide the model path.\n")
    parser.add_argument("-n", "--name", type=str, default='training_race_1',
                        help="Name of the training.")
    parser.add_argument("-s", "--validation_split", type=float, default=0.2,
                        help="Validation split. Must be between 0 and 1.")
    parser.add_argument("-e", "--nb_epochs", type=int, default=20,
                        help="Number of epochs of the training.")
    parser.add_argument("-r", "--random_seed", type=int, default=42,
                        help="Random seed used to shuffle dataset.")
    return parser.parse_args()


class TrainModel:
    def __init__(self, labels_path, name='training_race_1', validation_split=0.2, nb_epochs=2, seed=42):
        tf.random.set_seed(seed)
        random.seed(seed)
        self.images_json, self.features, self.directions_labels, self.speeds_labels = None, None, None, None
        self.images_dir = None
        self.validation_split = validation_split
        self.nb_epochs = nb_epochs

        self.model = None
        self.output_path = f"{name}/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

        self._get_and_save_json(labels_path)
        self._get_feat_labels()

    def _get_and_save_json(self, labels_path):
        labels_json = pathlib.Path(labels_path)
        self.images_dir = labels_json.parent

        with open(labels_json) as data:
            self.images_json = json.load(data)
        pathlib.Path(self.output_path).mkdir(parents=True, exist_ok=True)
        new_labels_path = f"{self.output_path}/labels.json"
        shutil.copy(labels_path, new_labels_path)

    def _get_feat_labels(self):
        features, speeds, directions = [], [], []
        images_values = list((self.images_json).values())
        random.shuffle(images_values)
        for v in images_values:
            features.append(self._get_image(str(self.images_dir / v['file_name'])))
            speeds.append(v['label']['label_speed'])
            directions.append(v['label']['label_direction'])

        self.images = np.asarray(features)
        self.directions_labels = np.asarray(directions, dtype='int16')
        self.speeds_labels = np.asarray(speeds, dtype='int16')

    def _get_image(self, image_path):
        image_str = tf.io.read_file(image_path)
        image = tf.image.decode_jpeg(image_str, channels=3).numpy() / 255.0
        return image
    # TODO def train preprocess ? tf.image brightness, saturation... or put it separately and create images ?

    def show_images(self, rows, cols):
        fig = plt.figure()
        for i, image in enumerate(self.images):
            if i == rows * cols:
                break
            ax = fig.add_subplot(rows, cols, i + 1)
            ax.imshow(image[:, :, :])
        plt.show()

    def train(self):
        self.model = model_setter.get_model_params()
        self.model.build(input_shape=(None, 96, 160, 3))
        self.model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                      optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), metrics=['accuracy'])
        self.model.summary()

        log_dir = f"logs/fit/{self.output_path}"
        checkpoint_path = f"{self.output_path}/cp-{{epoch:04d}}.ckpt"

        best_checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, monitor='val_loss', verbose=0,
                                                             mode='min', save_best_only=True)
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

        self.history = self.model.fit(self.images, [self.directions_labels, self.speeds_labels], epochs=self.nb_epochs,
                                      validation_split=self.validation_split,
                                 shuffle=True, verbose=1, callbacks=[best_checkpoint, tensorboard_callback])

    def predict(self):
        predictions = self.model.predict(self.images)
        speed_preds = []
        for elem in predictions[0]:
            speed_preds.append(np.argmax(elem))
        dir_preds = []
        for elem in predictions[1]:
            dir_preds.append(np.argmax(elem))
        return predictions, np.array(speed_preds), np.array(dir_preds)

    def show_balance(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 2, 1)
        ax.hist(self.directions_labels)
        ax.set_title("Histogram: Directions balance")
        ax = fig.add_subplot(1, 2, 2)
        ax.hist(self.speeds_labels)
        ax.set_title("Histogram: Speeds balance")
        png_path = f"{self.output_path}/labels_histogram.png"
        fig.savefig(png_path)


if __name__ == '__main__':
    options = get_args()
    train_model = TrainModel(options.labels_path, name=options.name, validation_split=options.validation_split,
                             nb_epochs=options.nb_epochs, seed=options.seed)
    # train_model.show_images(5, 10)
    train_model.train()
    train_model.show_balance()
    # TODO README?
    # TODO evaluate and put results with model?

    # train_model.predict()

