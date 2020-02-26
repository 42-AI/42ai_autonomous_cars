import io
import itertools

import pandas as pd
import sklearn.metrics
import tensorflow as tf
import json
import matplotlib.pyplot as plt
import numpy as np


# TODO (pclement): use sklearn to get metrics between predictions and truth (self.labels_directions, self.speed)
# TODO (pclement): plot key metrics and confusion matrix
# TODO a voir si j en fais pas une classe ac train_model en init ? ou path vers model

def _evaluate(train_model):
    evaluation_path = f"{train_model.output_path}/evaluation.txt"
    evaluation = train_model.model.evaluate(x=train_model.test_images,
                                     y=[train_model.test_directions_labels, train_model.test_speeds_labels], verbose=0)
    evaluation_dic = {"loss": float(evaluation[0]),
                      "direction_loss": float(evaluation[1]), "speed_loss": float(evaluation[2]),
                      "direction_accuracy": float(evaluation[3]), "speed_accuracy": float(evaluation[4])}
    with open(evaluation_path, 'w', encoding='utf-8') as fd:
        json.dump(evaluation_dic, fd, indent=4)
    cm_directions = get_confusion_matrix(train_model, index=0)
    cm_speed = get_confusion_matrix(train_model, index=1)
    plot_confusion_matrix(cm_directions)
    # plot_confusion_matrix(cm_speed)


def get_confusion_matrix(train_model, index):
    if index == 0:
        test_labels = train_model.test_directions_labels
    else:
        test_labels = train_model.test_speeds_labels
    test_pred_raw = train_model.model.predict(train_model.test_images)
    test_pred = np.argmax(test_pred_raw[index], axis=1)

    cm = sklearn.metrics.confusion_matrix(test_labels, test_pred)
    return cm

def plot_confusion_matrix(cm):
    """
    Returns a matplotlib figure containing the plotted confusion matrix.

    Args:
      cm (array, shape = [n, n]): a confusion matrix of integer classes
      class_names (array, shape = [n]): String names of the integer classes
    """

    # TODO a voir si test labels et test_pred sont series


    figure = plt.figure(figsize=(8, 8))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title("Confusion matrix")
    plt.colorbar()
    # tick_marks = np.arange(len(class_names))
    # plt.xticks(tick_marks, class_names, rotation=45)
    # plt.yticks(tick_marks, class_names)

    # Normalize the confusion matrix.
    # cm = np.around(cm.astype('float') / cm.sum(axis=1)[:, np.newaxis], decimals=2)

    # Use white text if squares are dark; otherwise black.
    threshold = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
       color = "white" if cm[i, j] > threshold else "black"
       plt.text(j, i, cm[i, j], horizontalalignment="center", color=color)

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()
    return figure

def plot_to_image(figure):
    """Converts the matplotlib plot specified by 'figure' to a PNG image and
    returns it. The supplied figure is closed and inaccessible after this call."""
    # Save the plot to a PNG in memory.
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    # Closing the figure prevents it from being displayed directly inside
    # the notebook.
    plt.close(figure)
    buf.seek(0)
    # Convert PNG buffer to TF image
    image = tf.image.decode_png(buf.getvalue(), channels=4)
    # Add the batch dimension
    image = tf.expand_dims(image, 0)
    return image

def log_confusion_matrix(epoch, logs):
    file_writer_cm = tf.summary.create_file_writer(logdir + '/cm')

    # Use the model to predict the values from the validation dataset.
    test_pred_raw = model.predict(test_images)
    test_pred = np.argmax(test_pred_raw, axis=1)

    # Calculate the confusion matrix.
    cm = sklearn.metrics.confusion_matrix(test_labels, test_pred)
    # Log the confusion matrix as an image summary.
    figure = plot_confusion_matrix(cm, class_names=class_names)
    cm_image = plot_to_image(figure)

    # Log the confusion matrix as an image summary.
    with file_writer_cm.as_default():
        tf.summary.image("Confusion Matrix", cm_image, step=epoch)
