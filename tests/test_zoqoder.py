import pytest

from zoqoder.zoqoder import zotero_connect

__author__ = "Julian Irwin"
__copyright__ = "Julian Irwin"
__license__ = "MIT"

from secrets_zotero import api_key, library_id, library_type

def test_zoqoder_connect():
    zotero_connect(api_key, library_id, library_type)