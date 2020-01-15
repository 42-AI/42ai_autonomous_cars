## upload_to_db

Function `upload_to_db` read labels from a file, upload picture to s3 and labels to ES cluster.

How to test:
* Log on a computer at 42 (or ask database admin to allow your ip to access the cluster)
* Ask database admin to create a user for you with access to the s3 bucket
* create env variable on your machine as follow:
```
export PATATE_S3_KEY_ID="your_access_key_id"
export PATATE_S3_KEY="your_secret_key_code"
```
**MAKE SURE TO NEVER UPLOAD YOUR KEY TO GITHUB OR SIMILAR**
* Run the functional test:
Go at the root of the repository and `py.test .`
