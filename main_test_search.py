from get_data import search_picture
from pathlib import Path
import json


if __name__ == "__main__":
    file = "get_data/sample/simple_search.json"
    with Path(file).open(mode='r', encoding='utf-8') as fp:
        d_query = json.load(fp)
    search_picture.create_search_query_from_dict(d_query)
