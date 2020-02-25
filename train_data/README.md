# HOW TO TRAIN DATA

This file describes how to train data:
1. Context
2. How to run the program
3. Options
4. Output


## 1. Context 
The `multi_output_train.py` script trains a model from images in a local folder that is structured correctly.
In order to get this folder, use the `search_and_download.py` script. (see the README.md in the get_data folder).  
This how to considers that the user has used this script to create a `training_image` folder (this folder contains all 
the images and a json file that describes these all images and conatins the labels).

The `multi_output_train.py` takes as argument the path to the json file in the above mentioned folder and a few optional arguments.
It trains a model that can be reused, and create a few meta_data that can be used to evaluate the model.


## 2. How to run the program
You must have a correct environment preset (see set_up folder).  
Run the program as follow:

<pre>
multi_output_train.py [-h] [-n NAME] [-s VALIDATION_SPLIT]
                      [-t TEST_SPLIT] [-e NB_EPOCHS] [-r RANDOM_SEED]
                      labels_path
</pre>

The labels path is the only required arguments. So the minimum command is:  
- if you run it from the project root folder  
```python train_data/multi_output_train.py path_to_training_images/labels.json```
- if you run it from the `train_data` folder  
```PYTHONPATH='..' python multi_output_train.py ../get_data/training_images/labels.json```


## 3. Options
<pre>
-h, --help            show this help message and exit
-n NAME, --name NAME  Name of the training.
-s VALIDATION_SPLIT, --validation_split VALIDATION_SPLIT
                      Validation split. Must be between 0 and 1.
-t TEST_SPLIT, --test_split TEST_SPLIT
                      Test split. Must be between 0 and 1.
-e NB_EPOCHS, --nb_epochs NB_EPOCHS
                      Number of epochs of the training.
-r RANDOM_SEED, --random_seed RANDOM_SEED
                      Random seed used to shuffle dataset.
</pre>

More info:
- NAME: It will be used to create a folder containing the model trained.
- VALIDATION_SPLIT and TEST_SPLIT: They set the proportion of the images of the images training that will be used for validation and test.
- NB_EPOCHS: Defaults to 20 and can be changed if necessary.
- RANDOM_SEED: Defaults to 42. It is used to shuffle the images and randomized the training, validation and test sets. 


## 4. Output  
  
Running the script will create 2 folders: 
a) NAME/timestamp that contains the models
b) logs/fit/NAME/timestamp that contains the information used by tensorboard

### a) NAME/timestamp  
The NAME Folder will look something like this.
```tree training_race_1
training_race_1
└── 20200225-201046
    ├── cp-0001.ckpt
    │   ├── assets
    │   ├── saved_model.pb
    │   └── variables
    │       ├── variables.data-00000-of-00001
    │       └── variables.index
    ├── cp-0002.ckpt
    ├── cp-0003.ckpt
    ├── cp-0006.ckpt
    ├── cp-0010.ckpt
    ├── cp-0011.ckpt
    ├── cp-0017.ckpt
    ├── evaluation.txt
    ├── labels.json
    ├── labels_histogram.png
    └── params.json
```  



This folder contains several folders ending in ckpt. Those are the models. By default the last one had the best 
validation loss metrics. Note that all the .ckpt are folders but I didn't put their children here as there are the 
same as cp-0001.ckpt In this case, for this training of 20 epochs, the script saved a model at epoch 1, 2, 3, 6, 10, 
11 and 17. It only saves a model if the validation loss is better than the previous models saved. So in this case 
cp-0017.ckpt is the model where the validation loss was the lowest.

It also contains 4 files:
- labels.json: the json with all the images used to create the model.
- params.json: the params used to train the model with the given images
- labels_histogram.png: Histograms showing the label repartition to check if the dataset is well balanced.
- evalutation.txt: the results of evaluating the test dataset created from the initial dataset.


### b) logs/fit/NAME/timestamp 
This folder is created by tensorflow so that we can use Tensorboard to analyze the models.
Run `tensorboard --logdir logs/fit/NAME` to get access to more info on the models.