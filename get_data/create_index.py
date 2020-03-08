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
    parser.add_argument("-p", "--prod", action="store_true",
                        help=f'The created index is used for prod and take over the main index alias')
    return parser.parse_args()


def create_index():
    """
    Create a new index using the index mapping defined in the conf.
    If --prod, set alias to the index defined in cluster_conf file. All other index will be removed from this alias
    making the new index the one used for production.
    """
    args = get_args(create_index.__doc__)
    alias = ES_INDEX if args.prod else None
    es = es_utils.create_es_index(host_ip=ES_HOST_IP,
                                  host_port=ES_HOST_PORT,
                                  index_name=args.index,
                                  alias=alias,
                                  index_pattern="_all")
    if es is not None:
        if alias is not None:
            print(f'Index "{args.index}" created and defined as the new read/write index for alias "{ES_INDEX}"')
        else:
            print(f'Index "{args.index}" created.')


if __name__ == "__main__":
    create_index()
