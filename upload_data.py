import argparse

from get_data import upload_to_db as upload
from get_data import cluster_param


def _get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("label_file", type=str, help="Path to the json label file")
    parser.add_argument("-b", "--bucket", default=None,
                        help="If not defined, bucket name is retrived from the db_param.py file")
    parser.add_argument("-k", "--key", default=None,
                        help="Key prefix: upload to https://s3.amazonaws.com/<bucket_name>/<key_prefix><file_name>")
    parser.add_argument("-i", "--index", default=None,
                        help="If not defined, index name is retrived from the db_param.py file")
    return parser.parse_args()


if __name__ == "__main__":
    """Upload date (picture + label) to ES and S3 from a label.json file"""
    args = _get_args()
    label_file = args.label_file
    bucket_name = cluster_param.BUCKET_NAME if args.bucket is None else args.bucket
    key_prefix = args.key
    es_index_name = cluster_param.ES_INDEX if args.index is None else args.index
    es_ip_host = cluster_param.ES_HOST_IP
    es_port_host = cluster_param.ES_HOST_PORT
    upload.upload_to_db(label_file, bucket_name, es_ip_host, es_port_host, es_index_name,
                        overwrite=False, key_prefix=key_prefix)
