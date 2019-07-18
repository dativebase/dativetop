"""Tests for appending to an AOL, using real-world-like data
"""

import pprint

import dtaoldm.aol as aol_mod
import dtaoldm.domain as domain
import tests.utils as utils


OKA_OLD_INSTANCE, _ = domain.construct_old_instance(
    slug='oka',
    name='oka',
    url='http://127.0.0.1:5679/oka',
    leader='',
    state=domain.NOT_SYNCED_STATE,
    is_auto_syncing=False)


OKA_OLD_INSTANCE_UPDATED, _ = domain.construct_old_instance(
    slug=OKA_OLD_INSTANCE.slug,
    name='Okanagan OLD',
    url=OKA_OLD_INSTANCE.url,
    leader='http://realworldoldservice.com/oka',
    state=OKA_OLD_INSTANCE.state,
    is_auto_syncing=True)


def generate_initial_aol():
    aol = []
    for quad in  aol_mod.instance_to_quads(
            OKA_OLD_INSTANCE, domain.OLD_INSTANCE_TYPE):
        aol_mod.append_to_aol(aol, quad)
    return aol


def test_aol_appending():
    """Test that ...
    """
    initial_aol = generate_initial_aol()
    pprint.pprint(initial_aol)

    extracted_domain_entities = aol_mod.aol_to_domain_entities(
        initial_aol, domain.CONSTRUCTORS)
    extracted_old_instance = [
        oi for oi in extracted_domain_entities['old-instances']
        if oi.slug == OKA_OLD_INSTANCE.slug][0]

    # TODO: start here
    OKA_OLD_INSTANCE_UPDATED, _ = domain.construct_old_instance(

    assert extracted_old_instance == OKA_OLD_INSTANCE

