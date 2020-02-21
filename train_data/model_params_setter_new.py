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

    img_in = Input(shape=(96, 160, 3), name='img_in')
    x = img_in

    x = Convolution2D(2, (5, 5), strides=(2, 2), use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = Convolution2D(4, (5, 5), strides=(2, 2), use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = Dropout(.4)(x)
    x = Convolution2D(8, (5, 5), strides=(2, 2), use_bias=False)(x)
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

    # pk 3 et pas 5 ??
    out_dir = Dense(3, activation='softmax')(x)
    out_speed = Dense(2, activation='softmax')(x)

    model = tf.keras.models.Model(inputs=img_in, outputs=[out_dir, out_speed])

    return model


if __name__ == '__main__':
    model = get_model_params()
    # output_shape = model.compute_output_shape(input_shape=(None, 96, 160, 3))
    # print(output_shape)
    model.build(input_shape=(None, 96, 160, 3))
    model.summary()
