from ast import literal_eval

from haystack.inputs import AltParser, Raw
from haystack.query import SearchQuerySet


def word_search(word):

    data = SearchQuerySet().auto_query(word).values("company_name")
    count = data.count()
    results = []
    results = data[0:count]

    return results


def list_search(search_list):

    list_dict = literal_eval((search_list).strip("[]"))
    query_tag = ""
    for i in range(0, len(list_dict)):
        query_tag = (
            query_tag
            + " "
            + (list_dict[i]["column_name"])
            + ":"
            + (list_dict[i]["input_value"] + "~")
            + " "
            + (list_dict[i]["and_or_value"])
        )

    data = (
        SearchQuerySet()
        .filter(content=AltParser("edismax", Raw(f"{query_tag}")))
        .values("vendorcode", "vendorname", "vendorgroup", "amount", "dateoutstanding")
    )

    results = []
    results = data[0:]
    return results


def column_word_search(search_list):
    query_tag = ""
    for i in range(0, len(search_list)):
        if " " in search_list[i]["input_value"]:
            query_tag = (
                query_tag
                + " "
                + (search_list[i]["column_name"])
                + ":"
                + "'"
                + (search_list[i]["input_value"] + "'" + "~1")
            )
        else:
            query_tag = (
                query_tag
                + " "
                + (search_list[i]["column_name"])
                + ":"
                + (search_list[i]["input_value"] + "~2")
            )
    query_tag = query_tag.strip()
    data = SearchQuerySet().filter(content=AltParser("edismax", Raw(f"{query_tag}"))).values("company_name")
    results = []
    results = data[0:]

    return results
