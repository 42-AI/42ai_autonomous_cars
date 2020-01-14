# LABEL README

This file describes how the pictures shall be labeled


## How to fill the label

Label are first created when running the car with `get_data_xbox_pad.py`
1. Create a directory where you want to store the pictures for this session. For instance /user/workdir/session  
2. In this directory create a session_template.json file. This template will be used to pre-fill every pictures saved in 
   this directory. Example of a session_template.json file:
   ```
   {
     "event": "session_14012020",
     "track" : "piste1",
     "track_type": "single lane",
     "dataset": ["D1"],
     "comment": "night session"
   }
   ```
   - You can use to 'dataset' field to add all picture of this session to a dataset or to create a new dataset.
3. Check that the hardware_conf.json file describes well the car. The content of this file will be added to the label of
   of each picture.  
   This file shall be at the root of the repository.  
   Example:
   ```
   {
     "hardware": {
       "car": "patate",
       "version": 1,
       "computer": "Raspberry_Pi2",
       "camera": "Picam_v2"
     }
   }
   ```
4. Run the car with `get_data_xbox_pad.py` to collect data. This script will use the two templates described above and 
   add the following field:
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

## Label Template

```
{
  "img_id": "1517255696",
  "file_name": "0_0_1517255696.923487.jpg",
  "location": "get_data/sample",
  "raw": "true",
  "transformation": [],
  "color": "rgb",
  "timestamp": "2015-01-01T12:10:30Z",
  "upload_date": "2015-01-01T12:10:30Z",
  "event": "iron car",
  "track" : "iron-car-012018",
  "track_type": "double lane dash",
  "resolution": {
    "horizontal": 512,
    "vertical": 214
  },
  "hardware": {
    "car": "patate",
    "version": 1,
    "computer": "Raspberry_Pi2",
    "camera": "Picam_v2"
  },
  "label": {
    "direction": 0,
    "speed": 0,
    "raw_direction": 260,
    "raw_speed": 315
  },
  "dataset": ["D1", "D2"],
  "comment": "whatever you want to say about this picture"
}
```
