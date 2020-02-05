import argparse
import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

from get_data.src import upload_to_db as upload
from conf import cluster_conf


def _get_args(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("label_file", type=str, help="Path to the json label file")
    parser.add_argument("-b", "--bucket", default=None,
                        help="OPTIONAL. By default, bucket name is retrieved from the cluster_conf.py file")
    parser.add_argument("-k", "--key", default=None,
                        help="OPTIONAL. By default, key is automatically generated from the label. Final url of the "
                             "picture: https://s3.amazonaws.com/<bucket_name>/<key_prefix><file_name>)")
    parser.add_argument("-i", "--index", default=None,
                        help="OPTIONAL. By default, index name is retrieved from the cluster_conf.py file")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Force option will overwrite existing pictures and labels in S3 and ES with new one"
                             " if same img_id is found")
    return parser.parse_args()


def upload_data():
    """
    Upload date picture and label to S3 and ES from a label file (json format). The label file can contain one or
    a list of label.
    To see a label template, use the write_label_template.py function.
    You will need credential for the upload. Access keys shall be defined in the following environment variables:
    export PATATE_S3_KEY_ID="your_access_key_id"
    export PATATE_S3_KEY="your_secret_key_code"
    export ES_USER_ID="your_es_user_id"
    export ES_USER_PWD="your_es_password"
    """
    args = _get_args(upload_data.__doc__)
    label_file = args.label_file
    bucket_name = cluster_conf.BUCKET_NAME if args.bucket is None else args.bucket
    key_prefix = args.key
    es_index_name = cluster_conf.ES_INDEX if args.index is None else args.index
    es_ip_host = cluster_conf.ES_HOST_IP
    es_port_host = cluster_conf.ES_HOST_PORT
    upload.upload_to_db(label_file, bucket_name, es_ip_host, es_port_host, es_index_name,
                        overwrite=args.force, key_prefix=key_prefix)


if __name__ == "__main__":
    upload_data()
