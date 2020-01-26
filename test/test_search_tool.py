import pytest

from get_data import search_picture


@pytest.fixture()
def get_query_dic():
    return {
        "simple_match": {
            "type": "match",
            "field": "",
            "query": "test_create_label"
        },
        "keyword_match": {
            "type": "match",
            "field": "keyword",
            "query": "keyword_test_create_label"
        },
        "simple_range": {
            "type": "range",
            "field": "",
            "gte": "20191230",
            "lte": "20201230"
        }
    }


@pytest.fixture()
def get_dic_and_package_query(get_query_dic):
    def get_dic_package(field):
        d_query = {field: get_query_dic[field]}
        package_query = d_query[field].copy()
        package_query.pop("type")
        package_query.pop("field")
        return d_query, package_query
    return get_dic_package


def test_simple_match_search(get_dic_and_package_query):
    field = "simple_match"
    d_query, package_query = get_dic_and_package_query(field)
    expected_query = {
        "query": {
            "match": {
                field: package_query
            }
        }
    }
    print("d_query is: ", d_query)
    query = search_picture.create_search_query_from_dict(d_query)
    assert query.to_dict() == expected_query


def test_keyword_match_search(get_query_dic):
    field = "keyword_match"
    d_query = {field: get_query_dic[field]}
    package_query = d_query[field].copy()
    package_query.pop("type")
    package_query.pop("field")
    expected_query = {
        "query": {
            "match": {
                field + ".keyword": package_query
            }
        }
    }
    query = search_picture.create_search_query_from_dict(d_query)
    assert query.to_dict() == expected_query


def test_simple_range_search(get_query_dic):
    field = "simple_range"
    d_query = {field: get_query_dic[field]}
    package_query = d_query[field].copy()
    package_query.pop("type")
    package_query.pop("field")
    expected_query = {
        "query": {
            "range": {
                field: package_query
            }
        }
    }
    query = search_picture.create_search_query_from_dict(d_query)
    assert query.to_dict() == expected_query


def test_two_field_bool_search(get_dic_and_package_query):
    field_1 = "simple_match"
    field_2 = "keyword_match"
    d_query, package1 = get_dic_and_package_query(field_1)
    d2, package2 = get_dic_and_package_query(field_2)
    d_query.update(d2)
    expected_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {field_2 + ".keyword": package2}
                    },
                    {
                        "match": {field_1: package1}
                    }
                ]
            }
        }
    }
    query = search_picture.create_search_query_from_dict(d_query)
    assert query.to_dict() == expected_query
