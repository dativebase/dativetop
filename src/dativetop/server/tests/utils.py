"""AOL Tests Utils
"""

from collections import namedtuple
import os

import dativetop.aol as aol_mod
import dativetop.domain as domain


HERE = os.path.dirname(os.path.abspath(__file__))
RESOURCES_PATH = os.path.join(HERE, 'resources')
TMP_PATH = os.path.join(HERE, 'tmp')
for path in (TMP_PATH, RESOURCES_PATH):
    if not os.path.exists(path):
        os.mkdir(path)


Case = namedtuple('Case', 'sources, expected')


def generate_oi_quads():
    """Return a list of quads representing a single OI, OLDInstance.
    """
    old_instance, err = domain.construct_old_instance(
        slug='oka',
        name='Okanagan OLD',
        url='http://127.0.0.1:5679/oka',
        leader='',
        state=domain.NOT_SYNCED_STATE,
        is_auto_syncing=False)
    old_instance_quads = aol_mod.instance_to_quads(
        old_instance, domain.OLD_INSTANCE_TYPE)
    aol = []
    for quad in old_instance_quads:
        aol = aol_mod.append_to_aol(aol, quad)
    return aol


def generate_test_aol():
    """Return an AOL list of Appendable (tuple) instances
    (encoding 2 ``OLDInstance``s).
    """
    test_old_instance_1, err = domain.construct_old_instance(
        slug='oka',
        name='Okanagan OLD',
        url='http://127.0.0.1:5679/oka',
        leader='',
        state=domain.NOT_SYNCED_STATE,
        is_auto_syncing=False)
    test_old_instance_2, err = domain.construct_old_instance(
        slug='bla',
        name='Blackfoot OLD',
        url='http://127.0.0.1:5679/bla',
        leader='',
        state=domain.NOT_SYNCED_STATE,
        is_auto_syncing=False)
    old_instance_type = domain.DOMAIN_ENTITIES_TO_ENTITY_TYPES[
        type(test_old_instance_1)]
    test_old_instance_1_quads = aol_mod.instance_to_quads(
        test_old_instance_1, old_instance_type)
    test_old_instance_2_quads = aol_mod.instance_to_quads(
        test_old_instance_2, old_instance_type)
    aol = []
    for quad in test_old_instance_1_quads + test_old_instance_2_quads:
        aol = aol_mod.append_to_aol(aol, quad)
    return aol


def generate_large_test_aol(n_old_instances):
    """Return an AOL enxoding ``n_old_instances`` OLDInstances."""
    aol = []
    for _ in range(n_old_instances):
        test_old_instance, err = domain.construct_old_instance(
            slug='oka',
            name='Okanagan OLD',
            url='http://127.0.0.1:5679/oka',
            leader='',
            state=domain.NOT_SYNCED_STATE,
            is_auto_syncing=False)
        for quad in aol_mod.instance_to_quads(
                test_old_instance, domain.OLD_INSTANCE_TYPE):
            aol = aol_mod.append_to_aol(aol, quad)
    return aol


def remove_test_files(*test_files):
    for fp in test_files:
        try:
            os.remove(fp)
        except:
            pass
