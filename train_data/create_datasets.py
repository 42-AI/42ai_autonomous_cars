import argparse
import json
import pathlib

import matplotlib.pyplot as plt
import tensorflow as tf

from tensorflow.keras.layers import Convolution2D, BatchNormalization, Activation, Dropout, Flatten, Input, Dense


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("labels_path", type=str,
                        help="Provide the model path.\n")
    return parser.parse_args()

options = get_args()


tf.random.set_seed(42)


def get_images_json(labels_path):
    labels_json = pathlib.Path(options.labels_path)
    images_dir = labels_json.parent

    with open(labels_json) as data:
        images_json = json.load(data)
    return images_json, images_dir


images_json, images_dir = get_images_json(options.labels_path)


ds_size = len(images_json)
print(ds_size)


def dataset_generator():
    for k, v in images_json.items():
        image_path = images_dir / v['file_name']
        label_dir = v['label']['label_direction']
        label_speed = v['label']['label_speed']
        yield str(image_path), tf.convert_to_tensor([label_dir, label_speed])







BUFFER_SIZE = ds_size
TRAIN_SIZE = int(BUFFER_SIZE * 0.8)
# TRAIN_SIZE = BUFFER_SIZE
BATCH_SIZE = 16
NUM_EPOCHS = 10
steps_per_epoch = TRAIN_SIZE // BATCH_SIZE
validation_steps = (BUFFER_SIZE - TRAIN_SIZE) // BATCH_SIZE

print(BUFFER_SIZE, TRAIN_SIZE, NUM_EPOCHS, steps_per_epoch)


ds = tf.data.Dataset.from_generator(dataset_generator, (tf.string, tf.int16), output_shapes=(tf.TensorShape([]), tf.TensorShape([2])))

print("BOB")

def _get_image(image_path, labels):
    image_str = tf.io.read_file(image_path)
    image = tf.image.decode_jpeg(image_str, channels=3)
    normalized_image = tf.cast(image, tf.float32) / 255.0
    return normalized_image, labels


ds_all = ds.map(lambda x, y: _get_image(x, y), num_parallel_calls = 5).shuffle(buffer_size=ds_size, reshuffle_each_iteration=False)


# ds_all = ds.map(lambda x, y: (tf.image.decode_jpeg(tf.io.read_file(x), channels=3), y), num_parallel_calls=tf.data.experimental.AUTOTUNE)

# ds_all = ds_all.map(lambda x, y: (tf.cast(x, tf.float32) / 255.0, y)).shuffle(buffer_size=BUFFER_SIZE, reshuffle_each_iteration=False)



ds_train = ds_all.take(TRAIN_SIZE).repeat(NUM_EPOCHS)
ds_train = ds_train.batch(BATCH_SIZE).prefetch(5)


ds_validation = ds_all.skip(TRAIN_SIZE).repeat(NUM_EPOCHS).batch(3).prefetch(5)




def show_images(dataset, rows, cols):
    ds_show = dataset.shuffle(ds_size).batch(ds_size)
    batch = next(iter(ds_show))
    print(batch)
    images = batch[0]

    print(batch[0].shape, batch[1])
    fig = plt.figure()
    for i, image in enumerate(images):
        if i == rows * cols:
            break
        ax = fig.add_subplot(rows, cols, i + 1)
        ax.imshow(image[:, :, :])
    plt.show()



def get_model_params():
    # TODO (pclement): play with models this is Model from PatateV2

    # K.clear_session()
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

    out_dir = Dense(3, activation='softmax')(x)
    out_speed = Dense(2, activation='softmax')(x)

    model_parameters = {
        'model_name': "model_race_speed.h5",
        'model_inputs': [img_in],
        # 'model_outputs': [out_speed, out_dir],
    }
    return model_parameters


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
model.add(Dense(2, use_bias=False))
model.add(BatchNormalization())
model.add(Activation("relu"))
model.add(Dropout(.3))


# model = tf.keras.Model(inputs=model_parameters['model_inputs'])
model.build(input_shape=(None, 96, 160, 3))

model.compile(loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True), optimizer=tf.keras.optimizers.Adam(), metrics=['accuracy'])
# model.summary()

# best_checkpoint = tf.keras.callbacks.ModelCheckpoint(model_parameters['model_name'], monitor='val_loss', verbose=1,
# save_best_only=True, mode='min')

# steps_per_epoch = 3

print(TRAIN_SIZE, BATCH_SIZE, NUM_EPOCHS, validation_steps, steps_per_epoch, ds_size)
exit()
history = model.fit(ds_train, epochs=NUM_EPOCHS, shuffle=True,
                    validation_data=ds_validation,
                    validation_steps=validation_steps,
                    steps_per_epoch=steps_per_epoch,
                    verbose=1)





# spliter en train, validation, test
# mettre images dans bon folder

if __name__ == '__main__':
    # print(labels_path)
    # print(images_json)
    # print(ds)
    # show_images(ds_train, 5, 5)
    # models_params = get_model_params()
    # train(models_params)
    print("end")


