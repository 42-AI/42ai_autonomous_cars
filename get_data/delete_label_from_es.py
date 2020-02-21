import argparse
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1]))

from get_data.src import update_db
from conf import cluster_conf


def _get_args(description):
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("label_file", type=str, help="Path to the json label file")
    parser.add_argument("-i", "--index", default=None,
                        help="OPTIONAL. By default, index name is retrieved from the cluster_conf.py file")
    return parser.parse_args()


def delete_label_from_es():
    """
    Read a labels json file and delete all labels listed in this file from the Elasticsearch database. Only labels are
    deleted, not pictures.
    You will need credential for the upload. Access keys shall be defined in the following environment variables:
    export PATATE_ES_USER_ID="your_es_user_id"
    export PATATE_ES_USER_PWD="your_es_password"
    """
    args = _get_args(delete_label_from_es.__doc__)
    label_file = args.label_file
    es_index_name = cluster_conf.ES_INDEX if args.index is None else args.index
    update_db.delete_label_only(label_file=label_file, es_index=es_index_name)


if __name__ == "__main__":
    delete_label_from_es()
