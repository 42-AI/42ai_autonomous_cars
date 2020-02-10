import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

from get_data.src import label_handler, utils_fct

directory = "/Users/nvergnac/Documents/robocar"

for filename in os.listdir(directory):
    if filename.endswith(".jpg"): 
        new_filename = filename.rsplit('/', 1)
        print(os.path.join(directory, new_filename[-1]))
    else:
        continue