import argparse
from pathlib import Path

from get_data.utils import label_handler


def show_label_template():
    """
    Show a template of a picture's label as defined in the label_handler class. Use this function to check the current
    state of the label template.  
    """
    parser = argparse.ArgumentParser(description=str(show_label_template.__doc__),
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
    show_label_template()
