# HOW TO GET DATA

This file describes how to get new data:

0. Forewords
1. How the database works
2. Record pictures and create labels
3. Upload pictures and labels to the database
4. Manually relabelize pictures
5. Search and download pictures from the database
6. How to modify labels in the ES database
7. How to create/ delete dataset
8. Create a new index in Elasticsearch
9. BONUS TRACK - A small description of the database architecture

## Forewords

- Any function in this project should be run from the root folder, and not from a sub-folder like `get_data`.
- A log file is created in the logs folder when the following functions are called:
create_dataset.py	
create_index.py	
delete_dataset.py	
delete_label_from_es.py	
search_and_download.py	
upload_data.py	
- Path to the log folder is defined in `/conf/path.py`

Each log file lists all consecutive messages given during one run of a script.
A description of the different log messages levels can be found in the `../utils/config.py` file.


## 1. How the database works

The database (DB) is made of two parts: 
- An AWS S3 bucket to store pictures ; 
- An Elasticsearch (ES) cluster to store labels.  

You can access the Elasticsearch cluster through Kibana with the following link: 
https://124dd0d7eb3444ed82e5c16cf2321156.eu-west-1.aws.found.io:9243/

As of 2020, Jeremy Jauzion is the current administrator of the database and should be contacted to get the access credentials in order to be able to use/connect to AWS and ES.

How the DB works:  
- Each picture saved in S3 can have one or more associated labels in ES (for instance the same picture can have a label 
with 5 directions and another label with 3 directions. Hence the number of elements in S3 is less or equal to the nb
of elements in ES.
- Each picture in S3 has a unique id called `img_id` which is the timestamp of the picture
(eg: 20201231T15-45-55-123456)
- Labels stored in ES contain an "img_id" field with the id of the picture it refers to. A label in Elasticsearch is a 
json like document that looks similar to this:
```
{
  "img_id": "20200119T14-30-55-123456",
  "event": "iron car",
  "car_setting": {...},
  "label" : {
    "label_speed": 1,
    "label_direction": 2,
    ...
  },
  "label_fingerprint": "e170fca7848a59a815d2288802cc2832",
  ...
}
```
- Each label stored in ES has a unique id called `label_fingerprint`. This id is an hash of the following fields: 
`["img_id", "created_by", "label_direction", "label_speed", "nb_dir", "nb_speed"]`. 
This `label_fingerprint` shall be unique among the labels in the DB. If two labels have exactly the same value on those 6 fields, 
they will have the same hash, and hence, they will be considered duplicate and indexation will be refused.
- When searching and downloading pictures, only the missing pictures on the local drive are downloaded and a 
"labels.json" file is created. It contains all the labels of the pictures matching the search (including pictures already
 on the local drive and not downloaded) 
- This "labels.json" file regroups pictures labels in a dictionary. For example:  
  ```
  {
    "20201231T15-45-55-123456": {...},
    "20201231T15-45-56-456789": {...},
    ...
  }
  ```
  The key is the `img_id` and the value is the label, as stored in ES, associated to this picture. If the search returns
   several labels for a same `img_id`, only one label will be kept and a message is printed to warn the user.
- This "labels.json" file is 'disposable'. Every time someone wants to train a model, a request should be made to the ES database to get a .json file listing all the required pictures that will be used with a definite training set.


Note: The next chapters will present the different functions that can be used in the get_data folder. To get additional information about a function input parameters, simply add `-h` to access the help menu of the function:

ex: ```python function_name -h```

## 2. How to record pictures and create labels: `run_manual.py` and `write_label_template.py`

The `run_manual.py` script is used to run the car in manual mode (controlled with the xbox pad). Pictures are recorded during the run and for each recorded picture, a label is automatically created, stored in a json file that is then saved at the end of the run after pressing the 'A' key of the controller.

Steps:

1. Create a new session_template.json if none is found

2. Check that the content in the hardware_conf.json file correctly describes the car:

The content of this file will be added to the label of each picture.  
The location of this file is defined in the `path.py` file (and as of 04/2020, is found into the ../utils folder).
   Example of hardware conf file:
   ```
   {
     "car": "patate",
     "version": 1,
     "computer": "Raspberry_Pi2",
     "camera": "Picam_v2"
   }
   ```

3. Control and drive the car using `run_manual.py` to collect data:

The `run_manual.py` script must be directly run from the root 42ai_autonomous_cars folder:
> sudo python get_data/run_manual.py -o Path_to_output_directory
  
If the output folder provided to the script does not exist or has no session_template.json file, it will be automatically created.  
The session template contains information about the current session (event name, track type, ...etc) that is common to all pictures of this session.
     
The script will record each picture and create a corresponding label. All labels will be recorded into a single 
file that will be saved when the run is stopped using the 'A' key of the Xbox controller. 
There is no pause feature yet, so we have to then exit the program by pressing [q + enter] keys.
Each label will contain the session_template.json data and the hardware_conf.json data, as well as some information 
specific to each picture.  
To check the current fields used in the label format, you can print a template of a json file running the
`write_label_template.py` function from the root folder.

Every fields are automatically filled by the `run_manual.py` script.

4. Finally you might want to re labelized pictures using the Django tool launched from the `../DjangoInterface folder`. 
Images can then be uploaded to the database following the instruction in the next chapter.

Note: pictures can be uploaded to the database without relabelization.



## 3. How to upload pictures and labels to the database: `upload_data.py`

Use the function `upload_data.py` to read labels from a .json file, and upload pictures to s3 and labels to ES cluster.  

Note that you will need access credentials for Elasticsearch and s3. Ask admin for details.
The database visualization can be viewed through the `https://124dd0d7eb3444ed82e5c16cf2321156.eu-west-1.aws.found.io:9243/` link.

Your credentials shall be stored in the following environment variables (added into your .bashrc file for instance)
```
export PATATE_S3_KEY_ID="your_access_key_id"
export PATATE_S3_KEY="your_secret_key_code"
export PATATE_ES_USER_ID="your_es_user_id"
export PATATE_ES_USER_PWD="your_es_password"
```
**MAKE SURE TO NEVER UPLOAD YOUR CREDENTIALS TO GITHUB OR OTHER PUBLIC REPO**


## 4. How to manually relabelize and upload pictures: `../DjangoInterface/` `delete_labels_from_es.py` and `upload_to_db.py`

To learn how to run the GUI labelizer, check the README.md file in the Django interface folder: ../DjangoInterface.
Note: Any picture that is wanted to be in the relabelized set must have its label confirmed in the Django app even if the label has not changed. Otherwise, it will be ignored during the new database upload process. Once the relabelization is done, click the save button in the app to save a new .json file that
contains the new labels as well as the labels that will be deleted (this is done thanks to a field "to_delete" that is added in the picture label format). 


All you need to do now is using the `upload_to_db.py` scripts to upload the labels json file created with the Django UI.   
The script will upload the new labels and, for each label with the field "to_delete" set to True, delete the associated 
picture from S3 and the label from ES (the picture will only be deleted if no other label in the database is associated with it).  
Note that this will not delete from the database the original labels (the ones you download to be edited in Django). If 
you don't want to keep those original labels, you must use the `delete_labels_from_es.py` scripts with the original 
labels json file.



## 5. How to search and download pictures from the database: `search_and_download.py`

Use the function `search_and_download.py`. 
First, you must define your search query by modifying the search.json file located in the Queries folder.
It will look for pictures in the database matching your query, and check if they already are in the local pictures directory. If they aren't, you will be asked if you wish to download the missing pictures. If you decline, a new .json file listing the pictures found during the search will still be created.
A picture is missing if the "file_name", as stored in the db, can't be found in the pictures directory.

A json file sample can be found in `get_data/queries/search_json`.

For details on how this json works, see the docstring of the get_search_query_from_dict function in es_utils.  
For details on the ES query works, look at the doc: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html

NOTE: At the moment, there is a limitation in the number of returned pictures:  
Only the first 10 000 pictures found will be returned.


## 6. How to modify labels in the database

Normal procedure:
  1. Download the labels json file listing all the labels you want to modify
  2. Make a copy of the labels json file (`new_labels.json` for instance)
  3. Use the `/utils/modify_label_json_file.py` function to do your modifications on the `new_labels.json` file.
  You need to edit the function code with the modifications you want to do.
  4. Use the `upload_data.py` with option `--es_only` to upload the new labels (`new_labels.json`)
  5. Check the upload went OK
  6. Delete the old labels with the `delete_label_from_es.py` and the original file downloaded at step 1.
  
There is an easier solution if your modifications don't change the label fingerprint:
  1. Download the labels json file with all the labels you want to modify
  2. Use the `/utils/modify_label_json_file.py` function to apply your modifications on the labels.
  You need to edit the function code with the modifications you want to do.
  3. Use the `upload_data.py` with options `--force --es_only` to upload the modified labels and overwrite the old ones 
  (with same fingerprint)
  

## 7. How to create and delete dataset: `create_dataset.py` and `delete_dataset.py`

A dataset is a collection of labels tagged within a same dataset name. Each label have a field dataset containing the 
following information:  
```
"dataset": [
    {  
        "name": "name of the dataset",  
        "comment": "Why this dataset? How did you built it?",  
        "created_on_date": <date_of_creation>,  
        "query": "the_raw_query_used_to_gather_all_label_for_this_dataset"  
    },
    ...
]
```
**/!\ WARNING /!\ : Make sure the name of the dataset is unique when you create it. There is no verification, so if you 
name a dataset with an existing name, the labels will be appended to the existing one instead of creating a new dataset.**  
Note: you can only search a dataset by name. "comment", "created_on_date" and "query" are not searchable. 

### 7.1 Create a dataset
Use the function `create_dataset.py` in `get_data/` 
It interactively creates a dataset and add every label contained in the input file to this dataset. 
The input shall be a labels json file.
Once you have created the dataset, you will be ask for validation before any upload to ES."

### 7.2 Delete a dataset
Use the function `delete_dataset.py` in `get_data/`.


## 8. Create a new index in Elasticsearch: `create_index.py`
This function is only used to do tests and is not normally needed.

## 9. BONUS TRACK - Database architecture
The database is made of two parts: pictures are stored in an AWS S3 file storage service, associated labels are stored
in an Elasticsearch cluster.  
Labels contain the path to the pictures (ie: pictures urls).

The Elasticsearch server is an AWS EC2 instance within a VPC and public subnet. 
A Kibana instance runs in the same subnet as the Elasticsearch instance.  On the same instance as Kibana runs a Nginx 
server used as a reverse proxy to redirect traffic either to Kibana or Elasticsearch.  
Authentification is required to access ES cluster and Kibana.  

Access to the S3 bucket requires user authentification. Ask your admin to get your credentials.
