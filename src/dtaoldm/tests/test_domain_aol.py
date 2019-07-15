"""Tests for storing domain entities in the append-only log
"""

import dtaoldm.domain as domain
import dtaoldm.aol as aol_mod


def generate_test_aol():
    """Return an AOL encoding 2 OLDInstances, 1 DativeApp and 1 OLDService
    """
    old_instance_1, _ = domain.construct_old_instance(
        slug='oka',
        name='Okanagan OLD',
        url='http://127.0.0.1:5679/oka',
        leader='',
        state=domain.NOT_SYNCED_STATE,
        is_auto_syncing=False)
    old_instance_2, _ = domain.construct_old_instance(
        slug='bla',
        name='Blackfoot OLD',
        url='http://127.0.0.1:5679/bla',
        leader='',
        state=domain.NOT_SYNCED_STATE,
        is_auto_syncing=False)
    dative_app, _ = domain.construct_dative_app(
        url='http://127.0.0.1:5678/')
    old_service, _ = domain.construct_old_service(
        url='http://127.0.0.1:5679/')
    old_instance_1_quads = aol_mod.instance_to_quads(
        old_instance_1, domain.OLD_INSTANCE_TYPE)
    old_instance_2_quads = aol_mod.instance_to_quads(
        old_instance_2, domain.OLD_INSTANCE_TYPE)
    dative_app_quads = aol_mod.instance_to_quads(
        dative_app, domain.DATIVE_APP_TYPE)
    old_service_quads = aol_mod.instance_to_quads(
        old_service, domain.OLD_SERVICE_TYPE)
    quads = (
        old_instance_1_quads +
        old_instance_2_quads +
        dative_app_quads +
        old_service_quads)
    aol = []
    for quad in quads:
        aol = aol_mod.append_to_aol(aol, quad)
    domain_entities = {
        'old-instances': set([old_instance_1, old_instance_2]),
        'dative-apps': set([dative_app]),
        'old-services': set([old_service]),
    }
    return aol, domain_entities


def test_aol_roundtripping():
    """Test that we can store some domain entities in an AOL and then correctly
    extract them again as domain entities.
    """
    aol, true_domain_entities = generate_test_aol()
    computed_domain_entities = aol_mod.aol_to_domain_entities(
        aol, domain.CONSTRUCTORS)
    assert computed_domain_entities == true_domain_entities
