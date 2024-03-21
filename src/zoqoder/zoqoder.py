"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = zoqoder.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import logging

import pandas as pd
from pyzotero.zotero import Zotero
from itertools import chain
from functools import cache
from collections import defaultdict
from copy import deepcopy

from zoqoder import __version__

__author__ = "Julian Irwin"
__copyright__ = "Julian Irwin"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def zotero_connect(api_key, library_id, library_type):
    return Zotero(library_id=library_id, library_type=library_type, api_key=api_key)


DEFAULT_ANNOTATION_FIELDS = (
    "annotationText",
    "annotationComment",
    "annotationColor",
    "tags",
)


DEFAULT_DOCUMENT_FIELDS = (
    "key",
    "date",
    "creatorSummary",
    "title",
    "publicationTitle",
)


def tabulate_coding_summary_dataframe(
    zotero,
    annotation_items,
    document_fields=DEFAULT_DOCUMENT_FIELDS,
    annotation_fields=DEFAULT_ANNOTATION_FIELDS,
):
    table = tabulate_coding_summary(zotero, annotation_items, document_fields, annotation_fields)    
    return pd.DataFrame(table)

def tabulate_coding_summary(
    zotero,
    annotation_items,
    document_fields=DEFAULT_DOCUMENT_FIELDS,
    annotation_fields=DEFAULT_ANNOTATION_FIELDS,
):
    table = []
    key_table = tabulate_coding_summary_by_key(zotero, annotation_items)
    unique_tags = items_unique_tags(annotation_items)
    for document_key, annotation_keys_by_tag in key_table.items():
        tag_dict = {tag: [] for tag in unique_tags}
        document_item = item_by_key(zotero, document_key)
        _document_summary_dict = document_summary_dict(document_item, fields=document_fields)
        for tag, annotation_keys in annotation_keys_by_tag.items():
            for key in annotation_keys:
                item = item_by_key(zotero, key)
                tag_dict[tag].append(annotation_summary_text(item, fields=annotation_fields))
        table.append({**_document_summary_dict, **tag_dict})
    return table


def tabulate_coding_summary_by_key(zotero, annotation_items):
    all_unique_tags = items_unique_tags(annotation_items)
    table = defaultdict(lambda: {tag: [] for tag in all_unique_tags})
    for document_key, annotation_key in annotation_keys_by_document(zotero, annotation_items):
        for tag in item_unique_tags(item_by_key(zotero, annotation_key)):
            table[document_key][tag].append(annotation_key)
    return table


def tabulate_coding_summary_by_key_dataframe(zotero, annotation_items):
    table = tabulate_coding_summary_by_key(zotero, annotation_items)
    return pd.DataFrame.from_dict(table, orient="index")


def _replace_df_nans(df, replacement):
    return df.map(lambda x: replacement if pd.isnull(x) else x)


def annotation_summary_text(item, fields):
    return ", ".join(map(str, annotation_summary_dict(item, fields).values()))


def annotation_summary_dict(item, fields):
    filtered_item = _select_data_fields(item, fields)
    if "tags" in fields:
        filtered_item["tags"] = item_unique_tags(item)
    return filtered_item


def document_summary_dict(item, fields):
    filtered_item = _select_data_fields(item, fields)
    if "creatorSummary" in fields:
        filtered_item["creatorSummary"] = item.get("meta", {}).get("creatorSummary", "")
    return filtered_item


def _select_data_fields(item: dict[str], fields: list[str]) -> dict[str]:
    return {field: item["data"].get(field, "") for field in fields}


def item_unique_tags(item):
    return set([t["tag"] for t in item["data"]["tags"]])


def items_unique_tags(items):
    return set([t["tag"] for item in items for t in item["data"]["tags"]])


@cache
def item_by_key(zotero, key):
    query_result = zotero.items(itemKey=key)
    if len(query_result) == 1:
        return query_result[0]
    else:
        return {}


def annotation_keys_by_document(zotero, annotation_items) -> list[(str, str)]:
    return [(item_root(zotero, item)["key"], item["key"]) for item in annotation_items]


def group_annotation_keys_by_document(zotero, annotation_items) -> dict["str", "str"]:
    result = defaultdict(lambda: [])
    for item in annotation_items:
        result[item_root(zotero, item)["key"]].append(item["key"])
    return result


def keys_of(items):
    return [i["key"] for i in items]


def item_root(zotero, item):
    _logger.debug(f"item_root() {item['key']}")
    if has_parent(item):
        parent = item_parent(zotero, item)
        if not is_valid_item(parent):
            _logger.error(f'Parent {item["data"]["parentItem"]} of item {item["key"]} invalid.')
            return item
        else:
            return item_root(zotero, parent)
    else:
        return item

def is_valid_item(item):
    return "key" in item.keys()


def has_parent(item):
    return item["data"].get("parentItem", None) is not None


def item_parent(zotero, item):
    return item_by_key(zotero, item["data"]["parentItem"])


@cache
def all_annotations(zotero):
    return zotero.everything(zotero.items(itemType="annotation"))


def selected_annotations(zotero, tags=[], collections=[], highlights_only=False, all_annotations_cached=None):
    _logger.info("Filtering through annotations...")
    _annotations = all_annotations_cached
    if _annotations is None:
        _annotations = all_annotations(zotero)
    collection_keys = [collection_key(zotero, collection) for collection in collections]
    def filter_function(item):
        _is_highlight = is_highlight(item)
        _is_tagged = False
        _is_in_collection = False
        if tags:
            _is_tagged = any([has_tag(item_root(zotero, item), tag) for tag in tags])
        if collections:
            _is_in_collection = any([in_collection(zotero, item, key) for key in collection_keys])
        if highlights_only: 
            return _is_highlight and (_is_tagged or _is_in_collection)
        else:
            return _is_tagged or _is_in_collection
    res = list(filter(filter_function, _annotations))
    _logger.info("Found %d annotations.", len(res))
    return res


def is_highlight(annotation):
    return annotation.get("data", {}).get("annotationType", None) == "highlight"


def collection_key(zotero, collection_name):
    collections = zotero.collections()
    for collection in collections:
        if collection["data"]["name"] == collection_name:
            return collection["key"]
    raise ValueError(f"Collection {collection_name} not found.")


def in_collection(zotero, item, collection_key):
    return collection_key in item_root(zotero, item)["data"]["collections"]


def has_tag(item, tag):
    return tag in item_unique_tags(item)

def item_summary(item):
    return {
        "key": item.get("key", "NONE"),
        "itemType": item.get("data", {}).get("itemType", "NONE"),
        "parentItem": item.get("data", {}).get("parentItem", "NONE"),
        "tags": item.get("data", {}).get("tags", "NONE"),
    }