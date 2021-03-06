import argparse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).absolute().parents[1]))
from get_data.src import upload_to_db as upload
from get_data.src import update_db
from conf.cluster_conf import ES_HOST_PORT, ES_HOST_IP, ES_INDEX, LOG_INDEX, BUCKET_NAME
from utils import logger

log = logger.Logger().create(logger_name=Path(__file__).name)


def _get_args(description):
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("label_file", type=str, help="Path to the json label file")
    parser.add_argument("-b", "--bucket", default=BUCKET_NAME,
                        help="OPTIONAL. By default, bucket name is retrieved from the cluster_conf.py file")
    parser.add_argument("-k", "--key", default=None,
                        help="OPTIONAL. By default, key is automatically generated from the label. Final url of the "
                             "picture: https://s3.amazonaws.com/<bucket_name>/<key_prefix><file_name>)")
    parser.add_argument("-i", "--index", default=ES_INDEX,
                        help="OPTIONAL. By default, index name is retrieved from the cluster_conf.py file")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Force option will overwrite existing pictures and labels in S3 and ES with new one"
                             " if same img_id is found")
    parser.add_argument("-e", "--es_only", action="store_true",
                        help="Only upload labels to Elasticsearch cluster and doesn't upload pictures to S3."
                             "However, picture in S3 will still be removed based on instruction from the label_file.")
    return parser.parse_args()


def upload_data():
    """
    Upload and/or Delete picture in S3 and/or label in ES from a label file (json format). The label file shall be
    in the same folder as the picture to upload.
    The label file can contain one or more label in the form of a dictionary with the img_id as key for each label.
    To see a label template, use the write_label_template.py function.
    You will need credential for the upload. Access keys shall be defined in the following environment variables:
    export PATATE_S3_KEY_ID="your_access_key_id"
    export PATATE_S3_KEY="your_secret_key_code"
    export PATATE_ES_USER_ID="your_es_user_id"
    export PATATE_ES_USER_PWD="your_es_password"
    """
    args = _get_args(upload_data.__doc__)
    log.debug("Starting...")
    label_file = args.label_file
    bucket_name = None if args.es_only else args.bucket
    key_prefix = args.key
    update_db.delete_picture_and_label(label_file, es_index=args.index, bucket=bucket_name)
    upload.upload_to_db(label_file, ES_HOST_IP, ES_HOST_PORT, args.index,
                        bucket_name=bucket_name, overwrite=args.force, key_prefix=key_prefix)
    log.debug("Execution completed.")
    log.debug("Uploading log...")
    logger.Logger().upload_log(index=LOG_INDEX, es_host_ip=ES_HOST_IP, es_host_port=ES_HOST_PORT)


if __name__ == "__main__":
    upload_data()
