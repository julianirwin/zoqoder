import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from zoqoder.zoqoder import (
    zotero_connect,
    tabulate_coding_summary,
    tabulate_coding_summary_dataframe,
    tabulate_coding_summary_by_key,
    tabulate_coding_summary_by_key_dataframe,
    annotation_keys_by_document,
    group_annotation_keys_by_document,
    all_annotations,
    selected_annotations,
    item_parent,
    has_parent,
    item_root,
    item_by_key,
    item_unique_tags,
    items_unique_tags,
    is_highlight,
    item_summary,
    # annotation_data_filtered,
    # root_item_data_filtered
)
