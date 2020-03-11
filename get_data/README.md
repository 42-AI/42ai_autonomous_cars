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
8. BONUS TRACK - A small description of the database architecture

## Forewords

- All the function in this project shall be ran from the root folder, not from sub-folder like `get_data`.

## 1. How the database works

The database is made of two parts: An AWS S3 bucket to store pictures ; An Elasticsearch cluster to store labels.  

How does it work:  
- Each picture saved in S3 can have one or more associated labels in ES (for instance the same picture can have a label 
with 5 directions and another label with 3 directions. Hence the number of element in S3 is less or equal to the nb
of elements in ES.
- Each picture in S3 has a unique id called `img_id` which is the timestamp of the picture
(eg: 20201231T15-45-55-123456)
- Labels stored in ES contain an "img_id" field with the id of the picture it refers to. A label in Elasticsearch is a 
json like document that looks like something similar to this:
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
`["img_id", "created_by", "label_direction", "label_speed", "nb_dir", "nb_speed"]`. This `label_fingerprint` 
shall be unique among the labels in the DB. If two labels have exactly the same value on those 6 fields, 
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
- This "labels.json" file is 'disposable'. Every time one wants to train a model, a request should be made to the ES database to get a .json file listing all the required pictures that will be used to run a definite training set.


## 2. How to record pictures and create labels

The `run_manual.py` script is used to run the car in manual mode (it is controlled with the xbox pad). Pictures will be recorded during the run and for each recorded picture, a label is automatically created, stored in the json file.

Usage:
1. Check that the hardware_conf.json file correctly describes the car. 
The content of this file will be added to the label of each picture.  
The location of this file is defined in the `path.py` file.
   Example of hardware conf file:
   ```
   {
     "car": "patate",
     "version": 1,
     "computer": "Raspberry_Pi2",
     "camera": "Picam_v2"
   }
   ```
2. Control and drive the car using `run_manual.py` to collect data. Run `run_manual.py -h` for the usage.
The `run_manual.py` script must be launched directly from the root 42ai_autonomous_cars folder:
> sudo python get_data/run_manual.py -o Path_to_output_directory
  
If the output folder you provide to the script does not exist or has no session_template.json file,
it will be automatically created. The session template contains information about the session (event name, track 
type, ...etc) that are common to all the pictures of this session.
     
The script will record each picture and create the corresponding label. All labels will be saved in a single 
file until the run is stopped using the 'A' key of the Xbox controller. There is no pause feature yet, so we have to exit then the program by pressing q + enter.
Each label will contain the session_template.json data and the hardware_conf.json data, as well as some information 
specific to each picture.  
Example of info specific to a picture
 (the following might not be up to date. See the **Label Template** chapter for the actual template):
   ```
   {
     "img_id": "1517255696",
     "file_name": "0_0_1517255696.923487.jpg",
     "s3_bucket": "my-s3-bucket",
     "raw": "true",
     "color": "rgb",
     "timestamp": "2015-01-01T12:10:30Z",
     "resolution": {
       "horizontal": 512,
       "vertical": 214
     },
     "label": {
       "direction": 1,
       "speed": 0,
       "raw_direction": 260,
       "raw_speed": 315
     }
     "transformation": [],
     "upload_date": "",
     "label_fingerprint": "c072a1b9a16b633d6b3004c3edab7553"
   }
   ```
   Every fields are automatically filled by the script.
3. Then you might want to re labelized pictures and upload them to the database.
Note: right now, pictures are uploaded to the database before labelization.

### Label Template

To check the actual state of the label format, you can print a template of a json file using 
`write_label_template.py` (use `--help` for usage)


## 3. How to upload pictures and labels to the database 

Use the function `upload_data.py` to read labels from a file, upload picture to s3 and labels to ES cluster.  
See usage with `-h` option.

Note that you will need credential for Elasticsearch and s3. Ask admin for details.

Your credentials shall be stored in the following environment variables (added into your .bashrc file for instance)
```
export PATATE_S3_KEY_ID="your_access_key_id"
export PATATE_S3_KEY="your_secret_key_code"
export PATATE_ES_USER_ID="your_es_user_id"
export PATATE_ES_USER_PWD="your_es_password"
```
You can access Kibana at the following address: https://patate-db.com/
and log in by entering your PATATE_ES_USER_ID and PATATE_ES_USER_PWD.

**MAKE SURE TO NEVER UPLOAD YOUR CREDENTIALS TO GITHUB OR OTHER PUBLIC REPO**


## 4. How to re lablize pictures manually

To learn how to run the GUI labelizer, see the README.md in the Django interface folder.
  
Once you have re-labelized pictures and/or selected pictures to be deleted, you can download the new 
labels json file from the GUI. This file contains the new labels and the label that shall be deleted 
(a field "to_delete" is added in the label). All you need to do now is delete the modified labels + pictures and upload the new labels json file by respectively running the `delete_labels_from_es.py` and `upload_to_db.py` scripts.  

The script will upload the new label and, for each label with the field "to_delete" set to True, delete the associated 
picture from S3 and the label from ES. Note: the picture will only be deleted if no other label in the database points 
to it.

## 5. How to search and download pictures from the database

Use the function `search_and_download.py`. 
First, you must define your search query by modifying the search.json file located in the Queries folder.
It will look for pictures in the database matching your query and if they are already in the local picture directory, 
if not, you will be asked to download the missing pictures or not. If you decline, a new .json file listing the pictures found during the search will still be created.
A picture is missing if the "file_name", as stored in the db, can't be found in the pictures directory.
See usage with `-h` option for details.

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
  
There is a easier solution if your modifications don't change the label fingerprint:
  1. Download the labels json file with all the labels you want to modify
  2. Use the `/utils/modify_label_json_file.py` function to apply your modifications on the labels.
  You need to edit the function code with the modifications you want to do.
  3. Use the `upload_data.py` with options `--force --es_only` to upload the modified labels and overwrite the old ones 
  (with same fingerprint)
  

## 7. How to create and delete dataset

A dataset is a collection of labels tagged with a same dataset name. Each label have a field dataset containing the 
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
Use the function `create_dataset.py` in `get_data/` and follow the instruction (use `-h` to see usage). 

### 7.2 Delete a dataset
Use the function `delete_dataset.py` in `get_data/` and follow the instruction (use `-h` to see usage). 


## 8. BONUS TRACK - Database architecture
The database is made of two parts: pictures are stored in an AWS S3 file storage service, associated labels are stored
in an Elasticsearch cluster.  
Labels contain the path to the pictures (ie: pictures urls).

The Elasticsearch server is an AWS EC2 instance within a VPC and public subnet. 
A Kibana instance runs in the same subnet as the Elasticsearch instance.  On the same instance as Kibana runs a Nginx 
server used as a reverse proxy to redirect traffic either to Kibana or Elasticsearch.  
Authentification is required to access ES cluster and Kibana.  

Access to the S3 bucket requires user authentification.
