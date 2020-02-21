from datetime import datetime
import argparse
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).absolute().parents[1]))

from get_data.src import es_utils
from conf.cluster_conf import ES_HOST_IP, ES_HOST_PORT, ES_INDEX


def get_args(description):
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--index", type=str, default=f'{ES_INDEX}-{datetime.now().strftime("%y%m%d")}',
                        help=f'Name of the new index. By default : "{ES_INDEX}-today_date"')
    return parser.parse_args()


def create_index():
    """Create a new index and set alias to the index defined in cluster_conf file and set the
    new index as the write index for this alias."""
    CURRENT_WRITE_INDEX = "patate-db-200209"
    args = get_args(create_index.__doc__)
    es = es_utils.create_es_index(host_ip=ES_HOST_IP,
                             host_port=ES_HOST_PORT,
                             index_name=args.index,
                             alias=ES_INDEX,
                             is_write_index=True,
                             current_write_index=CURRENT_WRITE_INDEX)
    if es is not None:
        print(f'Index "{args.index}" created and defined as the new write index for alias "{ES_INDEX}"')


if __name__ == "__main__":
    create_index()
