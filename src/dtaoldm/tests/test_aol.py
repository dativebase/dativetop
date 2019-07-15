"""AOL Tests
"""

import os
from pathlib import Path

import dtaoldm.aol as aol_mod
import tests.utils as utils


def test_aol_persistence():
    """Test that ``persist_aol`` works correctly when the entire AOL is written
    to disk in one go, and when it is performed in stages, i.e., with an
    initial write and a subsequent append.
    """
    try:
        test_aol = utils.generate_test_aol()
        path_write = os.path.join(utils.TMP_PATH, 'aol-write.txt')
        path_write_append = os.path.join(utils.TMP_PATH, 'aol-write-append.txt')
        aol_mod.persist_aol(test_aol, path_write)
        aol_mod.persist_aol(test_aol[:5], path_write_append)
        aol_mod.persist_aol(test_aol, path_write_append)
        with open(path_write, 'r') as fh_w, open(path_write_append, 'r') as fh_wa:
            assert fh_w.read() == fh_wa.read()
    finally:
        utils.remove_test_files(path_write, path_write_append)


def test_aol_persistence_existing_empty_file():
    """Test that ``persist_aol`` works when there is already an empty file at
    the destination path.
    """
    try:
        test_aol = utils.generate_test_aol()
        path = os.path.join(utils.TMP_PATH, 'aol-initially-empty.txt')
        path_new = os.path.join(utils.TMP_PATH, 'aol.txt')
        Path(path).touch()
        aol_mod.persist_aol(test_aol, path)
        aol_mod.persist_aol(test_aol, path_new)
        with open(path_new, 'r') as fh_n, open(path, 'r') as fh:
            assert fh_n.read() == fh.read()
    finally:
        utils.remove_test_files(path, path_new)
