import argparse
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1]))

from get_data.src import get_from_db
from utils import logger

log = logger.Logger().create(logger_name=Path(__file__).name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search picture in the database according to a query json file and "
                                                 "download missing picture in the picture dir.\nA picture is missing if"
                                                 " the 'file_name', as stored in the db, can't be found in picture_dir.")
    parser.add_argument("-q", "--query", required=True, type=str,
                        help="Path to the input file, json format, containing the search parameters")
    parser.add_argument("-p", "--picture_dir", required=True, type=str, default=None,
                        help="Path to the picture directory where to download missing picture")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    args = parser.parse_args()
    log.debug("Starting...")
    get_from_db.search_and_download(query_json=args.query, picture_dir=args.picture_dir,
                                    verbose=1 if not args.verbose else 2)
    log.debug("Execution completed.")

