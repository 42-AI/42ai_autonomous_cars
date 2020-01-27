import argparse

from get_data import get_from_db as dl


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search picture in the database according to a json_file")
    parser.add_argument("file", type=str, help="Path to the input file, json format, containing the search parameters")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Path to the output file where to save the list of picture")
    args = parser.parse_args()
    dl.find_picture_in_db(args.file, args.output)

