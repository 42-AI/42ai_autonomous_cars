from pathlib import Path
import json

from get_data.src import label_handler as lh
from conf.path import SESSION_TEMPLATE_NAME, CACHE_DIR


def _get_cached_session_template():
    """
    Note: if cached template is not up to date with session template definition, undetermined behaviour...
    TODO: [jj] check if cached template is ok vs default session_template
    :return:
    """
    default_template = lh.Label().get_default_session_template()
    try:
        template_file = Path(CACHE_DIR) / SESSION_TEMPLATE_NAME
        with template_file.open(mode='r', encoding='utf-8') as fp:
            template = json.load(fp)
    except FileNotFoundError:
        Path(CACHE_DIR).mkdir(exist_ok=True)
        template = default_template
    return template


def _user_edit_template(template):
    action = None
    while action != "":
        print(f'Session template:\n{json.dumps(template, indent=4)}')
        while action not in ["", "e", "i"]:
            action = input("Press enter to proceed with this template. "
                           "To edit the template, type 'e' for manual edit or 'i' for interactive edit.\n")
        if action == "e":
            while action != "":
                action = input('Type `field:value` to change a specific field (value will be stored as a string).'
                               'Press enter to stop editing.\n')
                if action != "":
                    edit = action.split(":")
                    try:
                        template[edit[0]] = edit[1]
                    except KeyError:
                        print(f'Key "{edit[0]} is not valid.')
                    except IndexError:
                        print('Incorrect syntax')
            action = None
        if action == "i":
            for key, val in template.items():
                print(f'"{key}":{val},')
                new = input(f'Type in new "{key}" value (Press enter to keep current value):\n')
                if new != "":
                    template[key] = new
            action = None
    return template


def init_picture_folder(picture_dir):
    template_file = Path(picture_dir) / SESSION_TEMPLATE_NAME
    if not template_file.is_file():
        picture_dir = Path(picture_dir)
        if not picture_dir.is_dir():
            picture_dir.mkdir(parents=True)
            print(f'Output folder "{picture_dir}" created.')
        template = _get_cached_session_template()
        template = _user_edit_template(template)
        with template_file.open(mode='w', encoding='utf-8') as fp:
            json.dump(template, fp, indent=4)
        print(f'Session template file created: "{template_file}"')
        cached_file = Path(CACHE_DIR)/SESSION_TEMPLATE_NAME
        with cached_file.open(mode='w', encoding='utf-8') as fp:
            json.dump(template, fp, indent=4)
    else:
        with template_file.open(mode='r', encoding='utf-8') as fp:
            template = json.load(fp)
        print(f'Session template file found:\n{json.dumps(template, indent=4)}')
