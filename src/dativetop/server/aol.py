"""Append-only Log: functionality for persisting domain entities as entities in
an append-only log.

"""

from collections import namedtuple
from datetime import datetime
import hashlib
import json
import pprint
from uuid import uuid4

from domain import (
    DativeApp,
    OLDInstance,
    OLDService,
    construct_dative_app,
    construct_old_instance,
    construct_old_service,
)


def get_now():
    return datetime.utcnow()


def get_now_str():
    return get_now().isoformat()


def get_json(thing):
    return json.dumps(thing)


def serialize_quad(quad):
    return get_json(quad)


def get_hash(string_thing):
    return hashlib.md5(string_thing.encode('utf8')).hexdigest()


def get_hash_of_quad(quad):
    return get_hash(serialize_quad(quad))


def get_hash_of_serialized_quad(serialized_quad):
    return get_hash(serialized_quad)


def get_uuid():
    return str(uuid4())


def get_existence_triple(entity_id):
    return (entity_id, 'exists', '')


Quad = namedtuple(
    'Quad', (
        'entity',
        'attribute',
        'value',
        'time'))


OLD_INSTANCE_TYPE = 'old-instance'
DATIVE_APP_TYPE = 'dative-app'
OLD_SERVICE_TYPE = 'old-service'

ENTITY_TYPES = (
    OLD_INSTANCE_TYPE,
    DATIVE_APP_TYPE,
    OLD_SERVICE_TYPE,
)

DOMAIN_ENTITIES_AND_ENTITY_TYPES = (
    (DativeApp, DATIVE_APP_TYPE),
    (OLDInstance, OLD_INSTANCE_TYPE),
    (OLDService, OLD_SERVICE_TYPE),
)

DOMAIN_ENTITIES_TO_ENTITY_TYPES = {
    a: b for a, b in DOMAIN_ENTITIES_AND_ENTITY_TYPES}

ENTITY_TYPES_TO_DOMAIN_ENTITIES = {
    b: a for a, b in DOMAIN_ENTITIES_AND_ENTITY_TYPES}


ENTITY_ATTRIBUTES = (
    'is-a',
    'has-slug',
    'has-name',
    'has-url',
    'has-leader',
    'has-state',
    'is-auto-syncing?',
)


def fiat_entity():
    """Create a new entity as a quad."""
    return Quad(
        entity=get_uuid(),
        attribute='has',
        value='being',
        time=get_now_str(),)


def fiat_attribute(entity_id, attribute, value):
    """Assert that the entity referenced by ``entity_id`` has the supplied
    ``attribute`` with value ``value`` at call time UTC.
    """
    return Quad(
        entity=entity_id,
        attribute=attribute,
        value=value,
        time=get_now_str(),)


def instance_to_quads(instance):
    """Given a namedtuple domain entity ``instance``, return a tuple of quads
    (4-tuples) that would be sufficient to represent that domain entity in the
    append-only log.
    """
    being_quad = fiat_entity()
    entity_id = being_quad.entity
    instance_type = DOMAIN_ENTITIES_TO_ENTITY_TYPES[type(instance)]
    type_quad = fiat_attribute(entity_id, 'is_a', instance_type)
    quads = [being_quad, type_quad]
    for attr in instance._fields:
        quad_attr = attr
        if not quad_attr.startswith('is_'):
            quad_attr = f'has_{quad_attr}'
        quads.append(
            fiat_attribute(entity_id, quad_attr, getattr(instance, attr)))
    return tuple(quads)



def get_aol():
    """TODO: get the append-only-log from persistence, i.e., disk."""
    return []


Appendable = namedtuple(
    'Appendable', ('quad', 'hash', 'integrated_hash'))


def add_to_aol(aol, quad):
    try:
        top_appendable = aol[-1]
    except IndexError:
        top_integrated_hash = None
    else:
        top_appendable = Appendable(*top_appendable)
        top_integrated_hash = top_appendable.integrated_hash
    serialized_quad = serialize_quad(quad)
    hash_of_quad = get_hash_of_serialized_quad(serialized_quad)
    integrated_hash_of_quad = get_hash(
        get_json((top_integrated_hash, hash_of_quad)))
    appendable = Appendable(*(quad, hash_of_quad, integrated_hash_of_quad))
    aol.append(appendable)
    return aol


if __name__ == '__main__':
    import pprint
    from domain import construct_old_instance, NOT_SYNCED_STATE

    test_old_instance, err = construct_old_instance(
        slug='oka',
        name='Okanagan OLD',
        url='http://127.0.0.1:5679/oka',
        leader='',
        state=NOT_SYNCED_STATE,
        is_auto_syncing=False)
    assert not err
    pprint.pprint(test_old_instance)

    old_instance_quads = instance_to_quads(test_old_instance)
    pprint.pprint(old_instance_quads)

    for quad in old_instance_quads:
        serialized_quad = serialize_quad(quad)
        hash_of_quad = get_hash_of_quad(quad)
        print(serialized_quad)
        print(hash_of_quad)
        print('\n')

    aol = []
    for quad in old_instance_quads:
        aol = add_to_aol(aol, quad)
    pprint.pprint(aol)
