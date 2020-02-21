import argparse
import json
import pathlib

import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

# import matplotlib.pyplot as plt
# import pandas as pd
#
# import tensorflow.keras.callbacks
# from tensorflow.keras.models import Model
# from tensorflow.keras.preprocessing.image import load_img
# from tensorflow.keras.preprocessing.image import img_to_array

from train_data import model_params_setter_new
from conf.path import TRAINING_IMAGES_DIRECTORY, VALIDATION_IMAGES_DIRECTORY



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("labels_path", type=str,
                        help="Provide the model path.\n")
    return parser.parse_args()


class TrainModel:
    def __init__(self, labels_path, model_params=None, seed=1, validation_split=0.8, batch_size=16, nb_epochs=10):
        self.images_json = None
        self.images_dir = None
        self.validation_split = validation_split
        self.batch_size = batch_size
        self.nb_epochs = nb_epochs

        self.ds_all = 0
        self.ds_size = 0
        self.ds_train = None
        self.ds_validation = None

        # self.images = None
        # self.labels_directions = None
        # self.labels_speed = None
        # self.model_name = model_params['name']
        # self.model_inputs = model_params['inputs']
        # self.model_outputs = model_params['outputs']
        self.model = None

        self._get_images_json(labels_path)

        tf.random.set_seed(seed)

    def _get_images_json(self, labels_path):
        labels_json = pathlib.Path(labels_path)
        self.images_dir = labels_json.parent

        with open(labels_json) as data:
            self.images_json = json.load(data)

        self.ds_size = len(self.images_json)

        # est ce qu'il faudrait pas mieux shuffle et split la ?

    def _dataset_generator(self):
        for k, v in self.images_json.items():
            image_path = self.images_dir / v['file_name']
            label_dir = v['label']['label_direction']
            label_speed = v['label']['label_speed']
            yield str(image_path), tf.convert_to_tensor([label_dir, label_speed])

    def _get_image(self, image_path, labels):
        image_str = tf.io.read_file(image_path)
        image = tf.image.decode_jpeg(image_str, channels=3)
        normalized_image = tf.cast(image, tf.float32) / 255.0
        return normalized_image, labels

    # def train preprocess ? tf.image brightness, saturation... or put it separately and create images ?

    def create_datasets(self):
        train_size = int(self.ds_size * self.validation_split)

        ds_path = tf.data.Dataset.from_generator(self._dataset_generator, (tf.string, tf.int16),
                                                 output_shapes=(tf.TensorShape([]), tf.TensorShape([2])))

        self.ds_all = ds_path.map(lambda x, y: self._get_image(x, y), num_parallel_calls=tf.data.experimental.AUTOTUNE
                             ).shuffle(buffer_size=self.ds_size, reshuffle_each_iteration=False)
        self.ds_train = self.ds_all.take(train_size).repeat(self.nb_epochs).batch(self.batch_size).prefetch(tf.data.experimental.AUTOTUNE)
        self.ds_validation = self.ds_all.skip(train_size).repeat(self.nb_epochs).batch(self.batch_size).prefetch(tf.data.experimental.AUTOTUNE)
        print(self.ds_all, self.ds_train, self.ds_validation)

    def show_images(self, rows, cols):
        if self.ds_all is None:
            print("No dataset created.")
            exit()
        ds_show = self.ds_all.shuffle(self.ds_size).batch(self.ds_size)
        batch = next(iter(ds_show))
        images = batch[0]

        print(batch[0].shape, batch[1])
        fig = plt.figure()
        for i, image in enumerate(images):
            if i == rows * cols:
                break
            ax = fig.add_subplot(rows, cols, i + 1)
            ax.imshow(image[:, :, :])
        plt.show()

    def train(self):
        self.model = model_params_setter_new.get_model_params()
        # self.model.build(input_shape=(None, 96, 160, 3))
        self.model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                      optimizer=tf.keras.optimizers.Adadelta(learning_rate=0.001), metrics=['accuracy'])
        self.model.summary()

        train_size = int(self.ds_size * self.validation_split)
        steps_per_epoch = train_size // self.batch_size
        validation_steps = (self.ds_size - train_size) // self.batch_size

        history = self.model.fit(self.ds_train, epochs=self.nb_epochs, steps_per_epoch=steps_per_epoch,
                                 #validation_data=self.ds_validation, validation_steps=validation_steps,
                                 shuffle=True, verbose=1)
        return history


    # @staticmethod
    # def _normalize_images(images):
    #     return np.array(images) / 255.0

    def _show_balance(self):
        labels_speed_df = pd.Series(self.labels_speed)
        print(labels_speed_df.value_counts(), labels_speed_df.describe())
        labels_directions_df = pd.Series(self.labels_directions)
        print(labels_directions_df.value_counts(), labels_directions_df.describe())
        # TODO (pclement): make graphs?

    # def load_images(self, images_dir, show_test=True, show_balance=False):
    #     images, labels_speed, labels_directions = [], [], []
    #     self.images_dir = images_dir
    #     for filename in random.shuffle(os.listdir(self.images_dir)):
    #         filepath = self.images_dir + '/' + filename
    #         # load an image from file
    #         image = load_img(filepath, target_size=(96, 160))
    #         # convert the image pixels to a numpy array
    #         image = img_to_array(image)
    #         # get image id + labels
    #         value_dir = float(filename.split('_')[1])
    #         value_speed = float(filename.split('_')[0])
    #         labels_directions.append(value_dir)
    #         labels_speed.append(value_speed)
    #         images.append(image)
    #         self.labels_directions = np.array(pd.get_dummies(labels_directions))
    #         self.labels_speed = np.array(pd.get_dummies(labels_speed))
    #     self.images = self._normalize_images(images)
    #     if show_test is True:
    #         print('Loaded Images and labels for training: {}'.format(len(self.images)))
    #         print("For the image below, direction label is: {} and speed label is {}".format(self.labels_directions[42],
    #                                                                                          self.labels_speed[42]))
    #         plt.imshow(self.images[42])
    #     if show_balance is True:
    #         self._show_balance()

    # def train(self):
    #     self.model = Model(inputs=self.model_inputs, outputs=self.model_outputs)
    #     self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    #     print(self.model.summary)
    #     best_checkpoint = tensorflow.keras.callbacks.ModelCheckpoint(self.model_name, monitor='val_loss', verbose=1,
    #                                                       save_best_only=True, mode='min')
    #     self.model.fit(self.images, [self.labels_speed, self.labels_directions],
    #                    batch_size=64, epochs=100, validation_split=0.2,
    #                    verbose=1, callbacks=[best_checkpoint])
    #     # TODO (pclement): use tensorboard

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
    options = get_args()


    train_model = TrainModel(options.labels_path)
    train_model.create_datasets()
    # train_model.show_images(5,5)
    history = train_model.train()
    # print(ddhistory)


    # train_model.load_images(TRAINING_IMAGES_DIRECTORY, show_test=True, show_balance=True)
    # train_model.train()
    # train_model.training_graph()
    # train_model.load_images(VALIDATION_IMAGES_DIRECTORY, show_test=True, show_balance=False)
    # train_model.predict()
