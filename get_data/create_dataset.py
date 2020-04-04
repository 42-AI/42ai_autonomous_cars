import argparse

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1]))

from conf.cluster_conf import ES_HOST_PORT, ES_HOST_IP, ES_INDEX, LOG_INDEX
from get_data.src import update_db
from utils import logger

log = logger.Logger().create(logger_name=Path(__file__).name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactively creates a dataset and add every label contained in the "
                                                 "input file to this dataset. The input shall be a labels json file. "
                                                 "Once you have created the dataset, you will be ask for validation "
                                                 "before the upload to ES.")
    parser.add_argument("label_file", type=str,
                        help="Label file, json format, containing all the label to add to the dataset.")
    parser.add_argument("-q", "--query_file", type=str, default=None,
                        help="Query file, json format, containing the raw query sent to Elasticsearch used to create "
                             "the label file.")
    parser.add_argument("-o", "--overwrite", action="store_true",
                        help="Overwrite the input label file (local file) to add the dataset in the file.")
    parser.add_argument("-i", "--index", type=str, default=ES_INDEX,
                        help="Name of the index. The default value is defined in the cluster conf file.")
    parser.add_argument("-ip", "--host_ip", type=str, default=ES_HOST_IP,
                        help="ip address of the ES host")
    parser.add_argument("-p", "--host_port", type=str, default=ES_HOST_PORT,
                        help="ES port on the host")
    args = parser.parse_args()
    log.debug("Starting create_dataset.py ...")
    update_db.create_dataset(label_json_file=args.label_file,
                             raw_query_file=args.query_file,
                             overwrite_input_file=args.overwrite,
                             es_index=args.index,
                             es_host_ip=args.host_ip,
                             es_host_port=args.host_port)
    log.debug("Execution completed.")
    log.debug("Uploading log...")
    logger.Logger().upload_log(index=LOG_INDEX, es_host_ip=ES_HOST_IP, es_host_port=ES_HOST_PORT)
