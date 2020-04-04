import argparse

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1]))

from conf.cluster_conf import ES_HOST_PORT, ES_HOST_IP, ES_INDEX, LOG_INDEX
from get_data.src import update_db
from utils import logger

log = logger.Logger().create(logger_name=Path(__file__).name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a dataset from the database. All labels with this dataset name"
                                                 " in their 'dataset.name' field will be updated. No labels nor pictures"
                                                 " are removed, only the dataset field of the labels is updated.")
    parser.add_argument("dataset_name", type=str,
                        help="Name of the dataset to delete")
    parser.add_argument("-i", "--index", type=str, default=ES_INDEX,
                        help="Name of the index. The default value is defined in the cluster conf file.")
    parser.add_argument("-ip", "--host_ip", type=str, default=ES_HOST_IP,
                        help="ip address of the ES host")
    parser.add_argument("-p", "--host_port", type=str, default=ES_HOST_PORT,
                        help="ES port on the host")
    args = parser.parse_args()
    log.debug("Starting...")
    update_db.delete_dataset(dataset_name=args.dataset_name,
                             es_index=args.index,
                             es_host_ip=args.host_ip,
                             es_host_port=args.host_port)
    log.debug("Execution completed.")
    log.debug("Uploading log...")
    logger.Logger().upload_log(index=LOG_INDEX, es_host_ip=ES_HOST_IP, es_host_port=ES_HOST_PORT)
