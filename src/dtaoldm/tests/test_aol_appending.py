"""Tests for appending to an AOL, using real-world-like data
"""

from collections import namedtuple
import pprint

import pytest

import dtaoldm.aol as sut
import dtaoldm.domain as domain
import dtaoldm.utils as u
import tests.utils as utils

OKA_OLD_ID = 'ee07263b-ce9c-401f-9f71-4fa69ef3836b'

OKA_OLD_INSTANCE, _ = domain.construct_old_instance(
    id=OKA_OLD_ID,
    slug='oka',
    name='oka',
    url='http://127.0.0.1:5679/oka',
    leader='',
    state=domain.NOT_SYNCED_STATE,
    is_auto_syncing=False)


oka_old_instance_updated = OKA_OLD_INSTANCE._asdict()
oka_old_instance_updated['name'] = 'Okanagan OLD'
oka_old_instance_updated['leader'] = 'http://realworldoldservice.com/oka'
oka_old_instance_updated['is_auto_syncing'] = True
OKA_OLD_INSTANCE_UPDATED, _ = domain.construct_old_instance(
    **oka_old_instance_updated)


def generate_initial_aol():
    aol = []
    for quad in sut.instance_to_quads(
            OKA_OLD_INSTANCE, domain.OLD_INSTANCE_TYPE):
        sut.append_to_aol(aol, quad)
    return aol


ChangesCase = namedtuple('ChangesCase', 'target, mergee, changes')
Apbl = namedtuple('Apbl', 'integrated_hash')


def aolit(*args):
    """Create a fake tester AOL using all of the args in ``args``."""
    aol = []
    for arg in args:
        sut.append_to_aol(aol, sut.Quad(arg, arg, arg, arg))
    return aol


@pytest.mark.parametrize(
    'target, mergee, changes', (

        # 1. No change
        ChangesCase(
            target =[Apbl('a'), Apbl('b'), Apbl('c'),],
            mergee =[Apbl('a'), Apbl('b'), Apbl('c'),],
            changes=[],),

        # 2. No conflict, new from target
        ChangesCase(
            target =[Apbl('a'), Apbl('b'), Apbl('c'), Apbl('X'),],
            mergee =[Apbl('a'), Apbl('b'), Apbl('c'),],
            changes=[],),

        # 3. No conflict, new from mergee
        ChangesCase(
            target =[Apbl('a'), Apbl('b'), Apbl('c'),],
            mergee =[Apbl('a'), Apbl('b'), Apbl('c'), Apbl('d'),],
            changes=[Apbl('d'),],),

        # 4. Conflict A, equal new
        ChangesCase(
            target =[Apbl('a'), Apbl('b'), Apbl('c'), Apbl('X'),],
            mergee =[Apbl('a'), Apbl('b'), Apbl('c'), Apbl('d'),],
            changes=[Apbl('d'),],),

        # 5. Conflict B, more target new
        ChangesCase(
            target =[Apbl('a'), Apbl('b'), Apbl('c'), Apbl('X'), Apbl('Y'),],
            mergee =[Apbl('a'), Apbl('b'), Apbl('c'), Apbl('d'),],
            changes=[Apbl('d'),],),

        # 6. Conflict C, more mergee new
        ChangesCase(
            target =[Apbl('a'), Apbl('b'), Apbl('c'), Apbl('X'),],
            mergee =[Apbl('a'), Apbl('b'), Apbl('c'), Apbl('d'), Apbl('e'),],
            changes=[Apbl('d'), Apbl('e'),],),

        # 1.i. Empty, no change
        ChangesCase(
            target =[],
            mergee =[],
            changes=[],),

        # 1.ii. Short, no change
        ChangesCase(
            target =[Apbl('a'),],
            mergee =[Apbl('a'),],
            changes=[],),

        # 2.i Short, no conflict, new from target
        ChangesCase(
            target =[Apbl('X'),],
            mergee =[],
            changes=[],),

        # 3.i Short, no conflict, new from mergee
        ChangesCase(
            target =[],
            mergee =[Apbl('d'),],
            changes=[Apbl('d'),],),

        # 4.i Short, conflict A, equal new
        ChangesCase(
            target =[Apbl('X'),],
            mergee =[Apbl('d'),],
            changes=[Apbl('d'),],),

        # 5.i Short, conflict B, more target new
        ChangesCase(
            target =[Apbl('X'), Apbl('Y'),],
            mergee =[Apbl('d'),],
            changes=[Apbl('d'),],),

        # 6.i Short, conflict C, more mergee new
        ChangesCase(
            target =[Apbl('X'),],
            mergee =[Apbl('d'), Apbl('e'),],
            changes=[Apbl('d'), Apbl('e'),],),

    )
)
def test_find_changes(target, mergee, changes):
    """Test that aol::find_changes works as expected."""
    assert sut.find_changes(target, mergee) == changes


MergeCase = namedtuple(
    'MergeCase', (
        'target',
        'mergee',
        'conflict_resolution_strategy',
        'diff_only',
        'merged',
        'err',
    )
)


@pytest.mark.parametrize(
    'target, mergee, conflict_resolution_strategy, diff_only, merged, err', (

        # 1. No change
        MergeCase(
            target=aolit('a', 'b', 'c',),
            mergee=aolit('a', 'b', 'c',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=aolit('a', 'b', 'c',),
            err=None,),

        # 2. No conflict, new from target
        MergeCase(
            target=aolit('a', 'b', 'c', 'X',),
            mergee=aolit('a', 'b', 'c',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=aolit('a', 'b', 'c', 'X',),
            err=None,),

        # 3. No conflict, new from mergee
        MergeCase(
            target=aolit('a', 'b', 'c',),
            mergee=aolit('a', 'b', 'c', 'd',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=aolit('a', 'b', 'c', 'd',),
            err=None,),

        # 4. Conflict A, equal new, ABORT
        MergeCase(
            target=aolit('a', 'b', 'c', 'X',),
            mergee=aolit('a', 'b', 'c', 'd',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 4. Conflict A, equal new, MERGE
        MergeCase(
            target=aolit('a', 'b', 'c', 'X'),
            mergee=aolit('a', 'b', 'c', 'd'),
            conflict_resolution_strategy='rebase',
            diff_only=False,
            merged=aolit('a', 'b', 'c', 'X', 'd'),
            err=None,),

        # 5. Conflict B, more target new, ABORT
        MergeCase(
            target=aolit('a', 'b', 'c', 'X', 'Y',),
            mergee=aolit('a', 'b', 'c', 'd',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 5. Conflict B, more target new, REBASE
        MergeCase(
            target=aolit('a', 'b', 'c', 'X', 'Y',),
            mergee=aolit('a', 'b', 'c', 'd',),
            conflict_resolution_strategy='rebase',
            diff_only=False,
            merged=aolit('a', 'b', 'c', 'X', 'Y', 'd',),
            err=None,),

        # 6. Conflict C, more mergee new, ABORT
        MergeCase(
            target=aolit('a', 'b', 'c', 'X',),
            mergee=aolit('a', 'b', 'c', 'd', 'e',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 6. Conflict C, more mergee new, REBASE
        MergeCase(
            target=aolit('a', 'b', 'c', 'X',),
            mergee=aolit('a', 'b', 'c', 'd', 'e',),
            conflict_resolution_strategy='rebase',
            diff_only=False,
            merged=aolit('a', 'b', 'c', 'X', 'd', 'e',),
            err=None,),

        # 1.i. Empty, no change
        MergeCase(
            target=aolit(),
             mergee=aolit(),
             conflict_resolution_strategy='abort',
             diff_only=False,
             merged=aolit(),
             err=None,),

        # 1.ii. Short, no change
        MergeCase(
            target=aolit('a',),
            mergee=aolit('a',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=aolit('a',),
            err=None,),

        # 2.i Short, no conflict, new from target
        MergeCase(
            target=aolit('X',),
            mergee=aolit(),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=aolit('X'),
            err=None,),

        # 3.i Short, no conflict, new from mergee
        MergeCase(
            target=aolit(),
            mergee=aolit('d',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=aolit('d',),
            err=None,),

        # 4.i Short, conflict A, equal new, ABORT
        MergeCase(
            target=aolit('X',),
            mergee=aolit('d',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 4.i Short, conflict A, equal new, REBASE
        MergeCase(
            target=aolit('X',),
            mergee=aolit('d',),
            conflict_resolution_strategy='rebase',
            diff_only=False,
            merged=aolit('X', 'd',),
            err=None,),

        # 5.i Short, conflict B, more target new, ABORT
        MergeCase(
            target=aolit('X', 'Y',),
            mergee=aolit('d',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 5.i Short, conflict B, more target new, REBASE
        MergeCase(
            target=aolit('X', 'Y',),
            mergee=aolit('d',),
            conflict_resolution_strategy='rebase',
            diff_only=False,
            merged=aolit('X', 'Y', 'd',),
            err=None,),

        # 6.i Short, conflict C, more mergee new, ABORT
        MergeCase(
            target=aolit('X',),
            mergee=aolit('d', 'e',),
            conflict_resolution_strategy='abort',
            diff_only=False,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 6.i Short, conflict C, more mergee new, REBASE
        MergeCase(
            target=aolit('X',),
            mergee=aolit('d', 'e',),
            conflict_resolution_strategy='rebase',
            diff_only=False,
            merged=aolit('X', 'd', 'e',),
            err=None,),

        # With diff_only=True

        # 1. No change
        MergeCase(
            target=aolit('a', 'b', 'c',),
            mergee=aolit('a', 'b', 'c',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=aolit(),
            err=None,),

        # 2. No conflict, new from target
        MergeCase(
            target=aolit('a', 'b', 'c', 'X',),
            mergee=aolit('a', 'b', 'c',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=aolit('a', 'b', 'c', 'X',)[-1:],
            err=None,),

        # 3. No conflict, new from mergee
        MergeCase(
            target=aolit('a', 'b', 'c',),
            mergee=aolit('a', 'b', 'c', 'd',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=[],
            err=None,),

        # 4. Conflict A, equal new, ABORT
        MergeCase(
            target=aolit('a', 'b', 'c', 'X',),
            mergee=aolit('a', 'b', 'c', 'd',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 4. Conflict A, equal new, MERGE
        MergeCase(
            target=aolit('a', 'b', 'c', 'X'),
            mergee=aolit('a', 'b', 'c', 'd'),
            conflict_resolution_strategy='rebase',
            diff_only=True,
            merged=aolit('a', 'b', 'c', 'X', 'd')[-2:],
            err=None,),

        # 5. Conflict B, more target new, ABORT
        MergeCase(
            target=aolit('a', 'b', 'c', 'X', 'Y',),
            mergee=aolit('a', 'b', 'c', 'd',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 5. Conflict B, more target new, REBASE
        MergeCase(
            target=aolit('a', 'b', 'c', 'X', 'Y',),
            mergee=aolit('a', 'b', 'c', 'd',),
            conflict_resolution_strategy='rebase',
            diff_only=True,
            merged=aolit('a', 'b', 'c', 'X', 'Y', 'd',)[-3:],
            err=None,),

        # 6. Conflict C, more mergee new, ABORT
        MergeCase(
            target=aolit('a', 'b', 'c', 'X',),
            mergee=aolit('a', 'b', 'c', 'd', 'e',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 6. Conflict C, more mergee new, REBASE
        MergeCase(
            target=aolit('a', 'b', 'c', 'X',),
            mergee=aolit('a', 'b', 'c', 'd', 'e',),
            conflict_resolution_strategy='rebase',
            diff_only=True,
            merged=aolit('a', 'b', 'c', 'X', 'd', 'e',)[-3:],
            err=None,),

        # 1.i. Empty, no change
        MergeCase(
            target=aolit(),
             mergee=aolit(),
             conflict_resolution_strategy='abort',
             diff_only=True,
             merged=aolit(),
             err=None,),

        # 1.ii. Short, no change
        MergeCase(
            target=aolit('a',),
            mergee=aolit('a',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=[],
            err=None,),

        # 2.i Short, no conflict, new from target
        MergeCase(
            target=aolit('X',),
            mergee=aolit(),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=aolit('X'),
            err=None,),

        # 3.i Short, no conflict, new from mergee
        MergeCase(
            target=aolit(),
            mergee=aolit('d',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=[],
            err=None,),

        # 4.i Short, conflict A, equal new, ABORT
        MergeCase(
            target=aolit('X',),
            mergee=aolit('d',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 4.i Short, conflict A, equal new, REBASE
        MergeCase(
            target=aolit('X',),
            mergee=aolit('d',),
            conflict_resolution_strategy='rebase',
            diff_only=True,
            merged=aolit('X', 'd',),
            err=None,),

        # 5.i Short, conflict B, more target new, ABORT
        MergeCase(
            target=aolit('X', 'Y',),
            mergee=aolit('d',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 5.i Short, conflict B, more target new, REBASE
        MergeCase(
            target=aolit('X', 'Y',),
            mergee=aolit('d',),
            conflict_resolution_strategy='rebase',
            diff_only=True,
            merged=aolit('X', 'Y', 'd',),
            err=None,),

        # 6.i Short, conflict C, more mergee new, ABORT
        MergeCase(
            target=aolit('X',),
            mergee=aolit('d', 'e',),
            conflict_resolution_strategy='abort',
            diff_only=True,
            merged=None,
            err=sut.NEED_REBASE_ERR,),

        # 6.i Short, conflict C, more mergee new, REBASE
        MergeCase(
            target=aolit('X',),
            mergee=aolit('d', 'e',),
            conflict_resolution_strategy='rebase',
            diff_only=True,
            merged=aolit('X', 'd', 'e',),
            err=None,),

    )
)
def test_merge_aols(target, mergee, conflict_resolution_strategy, diff_only,
                    merged, err):
    """Test that aol::find_changes works as expected."""
    actual_merged, actual_err = sut.merge_aols(
        target, mergee,
        conflict_resolution_strategy=conflict_resolution_strategy,
        diff_only=diff_only)
    if err:
        assert actual_err == err
    else:
        assert actual_merged == merged
