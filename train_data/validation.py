import itertools

import sklearn.metrics
import json
import matplotlib.pyplot as plt
import numpy as np


# TODO a voir si j en fais pas une classe ac train_model en init ? ou path vers model

def evaluate(train_model):
    evaluation_path = f"{train_model.output_path}/evaluation.txt"
    evaluation = train_model.model.evaluate(x=train_model.test_images,
                                            y=[train_model.test_directions_labels, train_model.test_speeds_labels],
                                            verbose=0)
    # dir_matt_coef, speed_matt_coef = get_matthews_coefficient(train_model)
    evaluation_dic = {"loss": float(evaluation[0]),
                      "direction_loss": float(evaluation[1]), "speed_loss": float(evaluation[2]),
                      "direction_accuracy": float(evaluation[3]), "speed_accuracy": float(evaluation[4]),
                      # "direction_matthews_coefficient": float(dir_matt_coef),
                      # "speed_matthews_coefficient": float(speed_matt_coef)
                      }
    with open(evaluation_path, 'w', encoding='utf-8') as fd:
        json.dump(evaluation_dic, fd, indent=4)

    cm_directions, directions_classes = get_confusion_matrix(train_model, index=0)
    cm_speeds, speeds_classes = get_confusion_matrix(train_model, index=1)
    figure = plot_confusion_matrix(cm_directions, directions_classes, "direction")
    figure.savefig(f"{train_model.output_path}/confusion_matrix_direction")
    figure = plot_confusion_matrix(cm_speeds, speeds_classes, "speed")
    figure.savefig(f"{train_model.output_path}/confusion_matrix_speed")


def get_matthews_coefficient(train_model):
    predictions = train_model.model.predict(np.array(train_model.test_images))
    speed_pred = np.argmax(predictions[1], axis=1)
    speed_true = train_model.test_speeds_labels

    dir_pred = np.argmax(predictions[0], axis=1)
    direction_true = train_model.test_directions_labels
    speed_matt_coef = sklearn.metrics.matthews_corrcoef(speed_true, np.array(speed_pred))
    dir_matt_coef = sklearn.metrics.matthews_corrcoef(direction_true, dir_pred)
    return dir_matt_coef, speed_matt_coef


def get_confusion_matrix(train_model, index):
    if index == 0:
        test_labels = train_model.test_directions_labels
    else:
        test_labels = train_model.test_speeds_labels
    test_pred_raw = train_model.model.predict(train_model.test_images)
    test_pred = np.argmax(test_pred_raw[index], axis=1)

    cm = sklearn.metrics.confusion_matrix(test_labels, test_pred)

    classes = np.unique(np.concatenate([test_labels, test_pred]))
    return cm, classes


def plot_confusion_matrix(cm, class_names, matrix_name):
    """
    Returns a matplotlib figure containing the plotted confusion matrix.

    Args:
      cm (array, shape = [n, n]): a confusion matrix of integer classes
      class_names (array, shape = [n]): String names of the integer classes
      matrix_name: String name of the matrix
    """
    figure = plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(f"Confusion matrix: {matrix_name}")
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names)
    plt.yticks(tick_marks, class_names)

    threshold = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        color = "white" if cm[i, j] > threshold else "black"
        plt.text(j, i, cm[i, j], horizontalalignment="center", color=color)

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    return figure
