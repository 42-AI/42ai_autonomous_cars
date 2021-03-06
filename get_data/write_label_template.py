import argparse
from pathlib import Path
import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

from get_data.src import label_handler


def write_label_template():
    """
    Show a template of a picture's label as defined in the label_handler class. Use this function to check the current
    state of the label template.  
    """
    parser = argparse.ArgumentParser(description=str(write_label_template.__doc__),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--output_file", type=str, default=None, help="Save the template to a file")
    args = parser.parse_args()
    label_template = label_handler.Label()
    print(f'Label template:\n{str(label_template)}')
    if args.output_file is not None:
        with Path(args.output_file).open(mode='w', encoding='utf-8') as fp:
            fp.write(str(label_template))
        print(f'Label template written to file "{args.output_file}".')


if __name__ == "__main__":
    write_label_template()
