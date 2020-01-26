import argparse

from get_data import find_pictures_in_db as find


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=str(find.find_picture.__doc__),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=str, help="Path to the input file, json format, containing the search parameters")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Path to the output file where to save the list of picture")
    args = parser.parse_args()
    find.find_picture(args.file, args.output)

