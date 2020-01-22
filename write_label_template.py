import argparse
from pathlib import Path

from get_data.utils import label_handler


def write_label_template():
    """
    Create a json file with a label as defined by in the label_handler class. Use this function to check the current
    state of the label template.  
    """
    parser = argparse.ArgumentParser(description=str(write_label_template.__doc__),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_file", type=str, help="path to the output file")
    args = parser.parse_args()
    label_template = label_handler.Label()
    with Path(args.output_file).open(mode='w', encoding='utf-8') as fp:
        fp.write(str(label_template))
    print(f'Label template:\n{str(label_template)}')
    print(f'Label template written to file "{args.output_file}".')


if __name__ == "__main__":
    write_label_template()
