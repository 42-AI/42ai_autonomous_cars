# HOW TO GET DATA

This file describes how to get data:
1. Record pictures and create labels
2. Upload pictures and labels to the database
3. Re labelize manually the pictures
4. Search for picture in the database
5. Download pictures
6. BONUS TRACK - A small description of the database architecture


## 1. How to record picture and create label

The script `collect_data.py` is used to run the car in manual mode (control with xbox pad). Picture will be recorded
during the run and for each recorded picture, a label is automatically created.  
Usage:
1. Create a directory where you want to store the pictures for this session. For instance /user/workdir/session  
2. In this directory create a session_template.json file. This template will be used to pre-fill every pictures' label. 
To get the expected session_template run `collect_data.py --session_template` or `-s`.  
Example of a session_template.json file:
   ```
   {
     "event": "session_14012020",
     "track" : "piste1",
     "track_type": "single lane",
     "dataset": ["D1"],
     "comment": "night session"
   }
   ```
   - For details about each of those fields see ...(label explanation file to do!)
3. Check that the hardware_conf.json file describes well the car. The content of this file will be added to the label of
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
4. Run the car with `collect_data.py` to collect data. Run `collect_data.py -h` for the usage. 
This script will record the pictures and create the label for each pictures. All the labels will be saved in a single 
file. Each labels will contains the session_template.json data and the hardware_conf data plus information specific 
to each pictures.  
Example of info specific to each picture
 (the following might not be up to date. See **Label Template** chapter for the actual template):
   ```
   {
     "img_id": "1517255696",
     "file_name": "0_0_1517255696.923487.jpg",
     "location": "../session",
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
   }
   ```
   All the field are automatically filled by the script.
5. Then you might want to re labelized the picture and upload them to the database

### Label Template

To check the actual state of the label format, you can print a template to a json file using the 
`write_label_template.py` (use `--help` for usage)


## 2. How to upload pictures and labels to the database 

Use the function `upload_to_db` to read labels from a file, upload picture to s3 and labels to ES cluster.  
See usage with `-h` option.

Note that you will need credential for Elasticsearch and s3. Ask admin for details.

Your credentials shall be stored in the following environment variable
```
export PATATE_S3_KEY_ID="your_access_key_id"
export PATATE_S3_KEY="your_secret_key_code"
export ES_USER_ID="your_es_user_id"
export ES_USER_PWD="your_es_password"
```
**MAKE SURE TO NEVER UPLOAD YOUR CREDENTIALS TO GITHUB OR OTHER PUBLIC REPO**


## 3. How to re lablize pictures manually

TO DO

## 4. How to search for picture in the database

Use the function `find_picture.py` to look for picture in the database.
See usage with `-h` option for details.

A json file sample can be found in `get_data/sample/search_json`.

For details on how this json works, see the docstring of the search function in es_utils

NOTE: At the moment, there is a limitation in the number of picture that will be return:  
Only the first 10 000 pictures found will be returned.


## 5. How to download pictures

TO DO


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
 
