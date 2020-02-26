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
    parser.add_argument("-s", "--validation_split", type=float, default=0.15,
                        help="Validation split. Must be between 0 and 1.")
    parser.add_argument("-t", "--test_split", type=float, default=0.15,
                        help="Test split. Must be between 0 and 1.")
    parser.add_argument("-e", "--nb_epochs", type=int, default=20,
                        help="Number of epochs of the training.")
    parser.add_argument("-r", "--random_seed", type=int, default=42,
                        help="Random seed used to shuffle dataset.")
    return parser.parse_args()


# noinspection PyUnresolvedReferences
class TrainModel:
    def __init__(self, labels_path, name='training_race_1',
                 validation_split=0.15, test_split=0.15, nb_epochs=20, seed=42):
        self.seed = seed
        tf.random.set_seed(seed)
        random.seed(seed)
        self.images_json = None
        self.features, self.directions_labels, self.speeds_labels = None, None, None
        self.test_features, self.test_directions_labels, self.test_speeds_labels = None, None, None
        self.images_dir = None
        self.validation_split = validation_split
        self.test_split = test_split
        self.nb_epochs = nb_epochs

        self.model = None
        self.history = None
        self.output_path = f"{name}/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

        self._set_images_json(labels_path)
        self._save_json(labels_path)
        self._save_params()
        self._set_feat_labels()

    def _set_images_json(self, labels_path):
        labels_json = pathlib.Path(labels_path)
        self.images_dir = labels_json.parent

        with open(labels_json) as data:
            self.images_json = json.load(data)

    def _save_json(self, labels_path):
        pathlib.Path(self.output_path).mkdir(parents=True, exist_ok=True)
        new_labels_path = f"{self.output_path}/labels.json"
        shutil.copy(labels_path, new_labels_path)

    def _save_params(self):
        pathlib.Path(self.output_path).mkdir(parents=True, exist_ok=True)
        params_path = f"{self.output_path}/params.json"
        params_dic = {"validation_split": self.validation_split, "test_split": self.test_split,
                      "nb_epochs": self.nb_epochs, "random_seed": self.seed}
        with open(params_path, 'w', encoding='utf-8') as fd:
            json.dump(params_dic, fd, indent=4)

    def _set_feat_labels(self):
        features, speeds, directions = [], [], []
        test_features, test_speeds, test_directions = [], [], []
        images_values = list(self.images_json.values())
        random.shuffle(images_values)
        for index, item in enumerate(images_values):
            if index < (1 - self.test_split) * len(images_values):
                features.append(self._get_image(str(self.images_dir / item['file_name'])))
                speeds.append(item['label']['label_speed'])
                directions.append(item['label']['label_direction'])
            else:
                test_features.append(self._get_image(str(self.images_dir / item['file_name'])))
                test_speeds.append(item['label']['label_speed'])
                test_directions.append(item['label']['label_direction'])

        self.images = np.asarray(features)
        self.directions_labels = np.asarray(directions, dtype='int16')
        self.speeds_labels = np.asarray(speeds, dtype='int16')
        self.test_images = np.asarray(features)
        self.test_directions_labels = np.asarray(directions, dtype='int16')
        self.test_speeds_labels = np.asarray(speeds, dtype='int16')

    @staticmethod
    def _get_image(image_path):
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
                                      validation_split=self.validation_split, shuffle=True, verbose=1,
                                      callbacks=[best_checkpoint, tensorboard_callback])
        if self.test_split > 0:
            self._evaluate()

    def _evaluate(self):
        evaluation_path = f"{self.output_path}/evaluation.txt"
        evaluation = self.model.evaluate(x=self.test_images,
                                         y=[self.test_directions_labels, self.test_speeds_labels], verbose=0)
        evaluation_dic = {"loss": float(evaluation[0]),
                          "direction_loss": float(evaluation[1]), "speed_loss": float(evaluation[2]),
                          "direction_accuracy": float(evaluation[3]), "speed_accuracy": float(evaluation[4])}
        with open(evaluation_path, 'w', encoding='utf-8') as fd:
            json.dump(evaluation_dic, fd, indent=4)

    def predict(self, image_path):
        image = self._get_image(image_path)
        predictions = self.model(image)
        # put as @tf.function if many
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
                             nb_epochs=options.nb_epochs, seed=options.random_seed, test_split=options.test_split)
    # train_model.show_images(5, 10)
    train_model.train()
    train_model.show_balance()
    # TODO evaluate: reflechir si ne pas utiliser lien vers folder avec images pour evaluer en fonction ?
    # TODO eventuellement dans evaluate mettre taille des datasets de train / validation / test
