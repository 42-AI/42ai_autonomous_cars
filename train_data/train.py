import os
import random
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt

import keras.backend as K
import keras.callbacks
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import Model, Sequential
from keras.layers import *


class TrainModel:
    def __init__(self, images_dir, model_params):
        self.images_dir = images_dir
        self.model_name = model_params['name']
        self.model_inputs = model_params['inputs']
        self.model_outputs = model_params['outputs']
        
    def load_images(self):
        images = []
        labels_speed = []
        labels_dir = []
        dir_list = os.listdir(self.images_dir)
        random.shuffle(dir_list)
        for filename in dir_list:
            filepath = self.images_dir + '/' + filename
            # load an image from file
            image = load_img(filepath, target_size=(96, 160))
            # convert the image pixels to a numpy array
            image = img_to_array(image)
            # get image id + labels
            value_dir = float(filename.split('_')[1])
            value_speed = float(filename.split('_')[0])
            labels_dir.append(value_dir)
            labels_speed.append(value_speed)
            images.append(image)
        return images, labels_speed, labels_dir

    @staticmethod
    def normalize_images(images):
        return images / 255.0


if __name__ == '__main__':
    dataset = "../../../../speed"
    # load images from both train and test groups
    images_directory = dataset+'/Train'
    train_model = TrainModel(images_directory)
    images, labels_speed, labels_dir = load_images(images_directory)
    print('Loaded Images and labels for training: {}'.format(len(images)))
    images =

#Normalise images
images = np.array(images)
images /= 255.0

#convert datas to dummyvalues
labels_dir = np.array(pd.get_dummies(labels_dir))
labels_speed = np.array(pd.get_dummies(labels_speed))

labels_dir[42], labels_speed[42], plt.imshow(images[42])




'''
Model from PatateV2
'''

K.clear_session()
#############################################################

img_in = Input(shape=(96, 160, 3), name='img_in')
x = img_in

x = Convolution2D(2, (5,5), strides=(2,2), use_bias=False)(x)
x = BatchNormalization()(x)
x = Activation("relu")(x)
x = Convolution2D(4, (5,5), strides=(2,2), use_bias=False)(x)
x = BatchNormalization()(x)
x = Activation("relu")(x)
x = Dropout(.4)(x)
x = Convolution2D(8, (5,5), strides=(2,2), use_bias=False)(x)
x = BatchNormalization()(x)
x = Activation("relu")(x)
x = Dropout(.5)(x)

x = Flatten(name='flattened')(x)

x = Dense(100, use_bias=False)(x)
x = BatchNormalization()(x)
x = Activation("relu")(x)
x = Dropout(.4)(x)
x = Dense(50, use_bias=False)(x)
x = BatchNormalization()(x)
x = Activation("relu")(x)
x = Dropout(.3)(x)

out_dir = Dense(3, activation='softmax')(x)
out_speed = Dense(2, activation='softmax')(x)


# Compile Model
model = Model(inputs=[img_in], outputs=[out_speed, out_dir])
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()


model_name="model_race_speed.h5"

#save best model if model improved
best_checkpoint = keras.callbacks.ModelCheckpoint(model_name, monitor='val_loss', verbose=1, save_best_only=True, mode='min')


h = model.fit(images, [labels_speed, labels_dir], batch_size=64, epochs=100, validation_split=0.2, verbose=1, callbacks=[best_checkpoint])


#print History graph
historydf = pd.DataFrame(h.history, index=h.epoch)
historydf.plot(ylim=(0, 1))


