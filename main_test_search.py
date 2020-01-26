from get_data import search_picture
from pathlib import Path
import json

from get_data.cluster_param import ES_INDEX


if __name__ == "__main__":
    file = "get_data/sample/simple_search.json"
    with Path(file).open(mode='r', encoding='utf-8') as fp:
        d_query = json.load(fp)
    s = search_picture.get_search_query_from_dict(ES_INDEX, d_query)
    search_picture.run_query(s)

