#  Patate/Data_processing/Training/3_directions_models_Opti_speed.ipynb

# noinspection PyPep8Naming
import tensorflow as tf
from tensorflow.keras.layers import Convolution2D, BatchNormalization, Activation, Dropout, Flatten, Input, Dense


def get_model_params():
    # TODO (pclement): play with models this is Model from PatateV2

    # TODO padding=same, activation in FC and activation with convolution ? ...

    # model = tf.keras.Sequential()
    # model.add(Convolution2D(2, (5, 5), strides=(2, 2), use_bias=False))
    # model.add(BatchNormalization())
    # model.add(Activation("relu"))
    # model.add(Convolution2D(4, (5, 5), strides=(2, 2), use_bias=False))
    # model.add(BatchNormalization())
    # model.add(Activation("relu"))
    # model.add(Dropout(.4))
    # model.add(Convolution2D(8, (5, 5), strides=(2, 2), use_bias=False))
    # model.add(BatchNormalization())
    # model.add(Activation("relu"))
    # model.add(Dropout(.5))
    #
    # model.add(Flatten(name='flattened'))
    #
    # model.add(Dense(100, use_bias=False))
    # model.add(BatchNormalization())
    # model.add(Activation("relu"))
    # model.add(Dropout(.4))
    # model.add(Dense(50, use_bias=False))
    # model.add(BatchNormalization())
    # model.add(Activation("relu"))
    # model.add(Dropout(.3))
    # model.add(Dense(5, activation='softmax'))
    # model.build(input_shape=(None, 96, 160, 3))
    #
    # return model

    tf.keras.backend.clear_session()


    model = tf.keras.Sequential()
    model.add(Convolution2D(2, (5, 5), strides=(2, 2), use_bias=False))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(Convolution2D(4, (5, 5), strides=(2, 2), use_bias=False))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(Dropout(.4))
    model.add(Convolution2D(8, (5, 5), strides=(2, 2), use_bias=False))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(Dropout(.5))

    model.add(Flatten(name='flattened'))

    model.add(Dense(100, use_bias=False))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(Dropout(.4))
    model.add(Dense(50, use_bias=False))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(Dropout(.3))

    # pk 3 et pas 5 ??
    model.add(Dense(5, activation='softmax'))

    return model


if __name__ == '__main__':
    model = get_model_params()
    # output_shape = model.compute_output_shape(input_shape=(None, 96, 160, 3))
    # print(output_shape)
    model.build(input_shape=(None, 96, 160, 3))
    model.summary()
