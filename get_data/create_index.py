from datetime import datetime
import argparse
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).absolute().parents[1]))

from get_data.src import es_utils
from conf.cluster_conf import ES_HOST_IP, ES_HOST_PORT, ES_INDEX, LOG_INDEX
from utils import logger

log = logger.Logger().create(logger_name=Path(__file__).name)


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
    log.debug("Starting...")
    alias = ES_INDEX if args.prod else None
    es_utils.create_es_index(host_ip=ES_HOST_IP,
                             host_port=ES_HOST_PORT,
                             index_name=args.index,
                             alias=alias,
                             index_pattern="_all")
    log.debug("Execution completed")
    log.debug("Uploading log...")
    logger.Logger().upload_log(index=LOG_INDEX, es_host_ip=ES_HOST_IP, es_host_port=ES_HOST_PORT)


if __name__ == "__main__":
    create_index()
