import tensorflow as tf
from tensorflow.keras.layers import Convolution2D, BatchNormalization, Activation, Dropout, Flatten, Input, Dense


def get_model_params():
    # TODO padding=same, activation in FC and activation with convolution ? ...

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

    out_dir = Dense(5, activation='softmax', name='direction')(x)
    out_speed = Dense(2, activation='softmax', name='speed')(x)

    model = tf.keras.models.Model(inputs=img_in, outputs=[out_dir, out_speed])

    return model


if __name__ == '__main__':
    model = get_model_params()
    model.build(input_shape=(None, 96, 160, 3))
    model.summary()
