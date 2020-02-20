# HOW TO GET DATA

This file describes how to get data:
1. How the database works
2. Record pictures and create labels
3. Upload pictures and labels to the database
4. Re labelize manually the pictures
5. Search and download pictures from the database
6. BONUS TRACK - A small description of the database architecture


## 1. How the database works

The database is made of two parts: AWS S3 bucket to store the pictures ; Elasticsearch cluster to store the labels.  

How does it works:  
- Each picture saved in S3 can have one or more associated labels in ES (for instance a same picture can have a label 
with 5 directions and another label with 3 directions. Hence the number of element dans S3 is less or equal to the nb
of element in ES.
- Each picture in S3 has a unique id called `img_id` which is the timestamp of the picture
(eg: 20201231T15-45-55-123456)
- Labels stored in ES contains a "img_id" field with the id of the picture it refers to. A label in Elasticsearch is a 
json like document that look to something like this:
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
- Each labels stored in ES has a unique id called `label_fingerprint`. This id is a hash of the following fields: 
`["img_id", "created_by", "label_direction", "label_speed", "nb_dir", "nb_speed"]`. This `label_fingerprint` 
shall be unique among the labels in the DB. If two labels have exactly the same value on those 6 fields, 
they will have the same hash, and hence, they will be considered duplicate and indexation will be refused.
- When searching and downloading pictures, only the missing picture on the local drive are downloaded and a 
"labels.json" file is created. It contains all the labels of the pictures matching the search (including picture already
 on local drive and not downloaded) 
- This "labels.json" file contains several pictures' label in a dictionary. For example:  
  ```
  {
    "20201231T15-45-55-123456": {...},
    "20201231T15-45-56-456789": {...},
    ...
  }
  ```
  The key is the `img_id` and the value is the label, as stored in ES, associated to this picture. If the search returns
   several labels for a same `img_id`, only one label will be kept and a message is printed to warn the user.
- This "labels.json" file is 'disposable'. Every time one wants to train a model, he shall request the ES database to 
get this file listing all the pictures required for the training he wished to run.


## 2. How to record picture and create labels

The script `run_manual.py` is used to run the car in manual mode (control with xbox pad). Picture will be recorded
during the run and for each recorded picture, a label is automatically created.  
Usage:
1. Check that the hardware_conf.json file describes well the car. The content of this file will be added to the label of
   of each picture.  
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
2. Run the car with `run_manual.py` to collect data. Run `run_manual.py -h` for the usage.   
  
   If the output folder you provide to the script does not exist or has no session_template.json file,
   it will be created automatically. The session template contains information about the session (event name, track 
   type, ...etc) that are common to all the pictures of this session.
     
   The script will record the pictures and create the label for each pictures. All the labels will be saved in a single 
file. Each labels will contains the session_template.json data and the hardware_conf.json data, plus information 
specific to each pictures.  
Example of info specific to each picture
 (the following might not be up to date. See **Label Template** chapter for the actual template):
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
   All the field are automatically filled by the script.
3. Then you might want to re labelized the picture and upload them to the database

### Label Template

To check the actual state of the label format, you can print a template to a json file using the 
`write_label_template.py` (use `--help` for usage)


## 3. How to upload pictures and labels to the database 

Use the function `upload_data.py` to read labels from a file, upload picture to s3 and labels to ES cluster.  
See usage with `-h` option.

Note that you will need credential for Elasticsearch and s3. Ask admin for details.

Your credentials shall be stored in the following environment variable
```
export PATATE_S3_KEY_ID="your_access_key_id"
export PATATE_S3_KEY="your_secret_key_code"
export PATATE_ES_USER_ID="your_es_user_id"
export PATATE_ES_USER_PWD="your_es_password"
```
**MAKE SURE TO NEVER UPLOAD YOUR CREDENTIALS TO GITHUB OR OTHER PUBLIC REPO**


## 4. How to re lablize pictures manually

To learn how to run the GUI labelizer, see the README.md in the Django interface folder.
  
Once you have re-labelized the pictures and/or selected pictures to be deleted, you can download the new 
labels json file from the GUI. This file contains the new labels and the label that shall be deleted 
(a field "to_delete" is added in the label). All you need to do to upload new label and delete label + picture 
selected is to run the `upload_to_db.py` scripts.  

The script will upload the new label and, for each label with the field "to_delete" set to True, delete the associated 
picture from S3 and the label from ES. Note: the picture will only be deleted if no other labels in the database points 
to it.

## 5. How to search and download pictures from the database

Use the function `search_and_download.py`. It will look for picture in the database matching your query, look if 
pictures are already in the local picture directory, and if not, it will download the missing picture.  
A picture is missing if the "file_name", as stored in the db, can't be found in picture directory.
See usage with `-h` option for details.

A json file sample can be found in `get_data/queries/search_json`.

For details on how this json works, see the docstring of the get_search_query_from_dict function in es_utils.  
For details on the ES query works, look at the doc: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html

NOTE: At the moment, there is a limitation in the number of picture that will be return:  
Only the first 10 000 pictures found will be returned.


## 6. BONUS TRACK - Database architecture
The database is made of two parts: the picture are stored in AWS S3 file storage service, associated labels are stored
in the Elasticsearch cluster.
The labels contain the path to the picture (ie: url of the picture)

The Elasticsearch server is an AWS EC2 instance within a VPC and public subnet. Access to the cluster is currently 
protected by ip only.  
A Kibana instance run in the same subnet as the Elasticsearch instance.  

Access to the S3 bucket requires user authentication.

Client script is used to :  
- Upload picture to S3 and label to ES
- Search for a list of picture matching certain criteria
- Download picture if not already on local disk
 
