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

from zoqoder import __version__

__author__ = "Julian Irwin"
__copyright__ = "Julian Irwin"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def zotero_connect(api_key, library_id, library_type):
    return Zotero(library_id=library_id, library_type=library_type, api_key=api_key)


def all_annotations(zotero):
    return zotero.everything(zotero.items(itemType="annotation"))


def root_item(zotero, item):
    if has_parent(item):
        return root_item(zotero, item_parent(zotero, item))
    else:
        return item


def has_parent(item):
    return item["data"].get("parentItem", None) is not None


def item_parent(zotero, item):
    return item_by_key(zotero, item["data"]["parentItem"])


def memoize(func):
    cache = dict()

    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return memoized_func


@memoize
def item_by_key(zotero, key):
    return zotero.items(itemKey=key)


# if __name__ == "__main__":
#     zotero = zotero_connect(api_key, library_id, library_type)
#     annotations = all_annotations(zotero)