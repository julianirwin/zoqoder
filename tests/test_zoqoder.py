import pytest

from zoqoder.zoqoder import zotero_connect, has_parent, item_by_key, item_parent, item_root

__author__ = "Julian Irwin"
__copyright__ = "Julian Irwin"
__license__ = "MIT"

from secrets_zotero import api_key, library_id, library_type


@pytest.fixture(scope="module")
def zotero():
    return zotero_connect(api_key, library_id, library_type)


@pytest.fixture(scope="module")
def attachment_item(zotero):
    return zotero.items(itemType="attachment")[0]


@pytest.fixture(scope="module")
def journal_item(zotero):
    return zotero.items(itemType="journalArticle")[0]


def test_zoqoder_connect():
    zotero_connect(api_key, library_id, library_type)


def test_attachment_has_parent(zotero, attachment_item):
    assert has_parent(attachment_item)


def test_article_does_not_have_parent(zotero, journal_item):
    assert not has_parent(journal_item)

def test_get_item_parent(zotero, attachment_item):
    item_parent(zotero, attachment_item)
    
def test_get_item_by_key(zotero, attachment_item):
    assert attachment_item["key"] == item_by_key(zotero, attachment_item["key"])["key"]

def test_get_item_by_missing_key(zotero):
    assert item_by_key(zotero, "HZGQFC3L").get("key", None) is None

def test_get_root_item(zotero, attachment_item):
    assert item_root(zotero, attachment_item)["key"] != attachment_item["key"]