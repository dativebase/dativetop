"""Event Attribute Value = eav.py

This was an attempt at a general mechanism for representing arbitrarily complex
dict/hash map-based data structures as EAV triples. The end result is a
``decompose`` function that converts a dict into a list of triples and the
converse ``assemble`` which produces a dict from a collection of triples. For
at least some data structures, it obeys the following invariant::


    >>> assemble(decompose(demo_data)) == demo_data

"""

import hashlib
import json
import pprint
from uuid import uuid4


def get_json_bytes(thing):
    return json.dumps(thing).encode('utf8')


def get_hash_bytes(thing):
    return hashlib.md5(get_json_bytes(thing)).hexdigest().encode('utf8')


def get_id():
    return str(uuid4())


def get_existence_triple(entity_id):
    return (entity_id, 'exists', '')


def decompose(structure, entity_id=None):
    entity_id = entity_id or get_id()
    ret = (get_existence_triple(entity_id),)
    for attr, val in structure.items():
        attr_id = get_id()
        sub_ret = (
            (attr_id, 'is a', 'attribute'),
            (entity_id, 'has attribute', attr_id),
            (attr_id, 'has name', attr),)
        if isinstance(val, dict):
            val_id = get_id()
            attr_has_val_tri = (attr_id, 'has value', val_id)
            sub_ret = sub_ret + (attr_has_val_tri,) + decompose(val, entity_id=val_id)
        else:
            sub_ret = sub_ret + ((attr_id, 'has value', val),)
        ret = ret + sub_ret
    return ret


def assemble(triples):
    entities = {}
    attributes = {}
    for (e, a, v) in triples:
        if a == 'exists' and v == '':
            entities[e] = {}
        elif a == 'is a' and v == 'attribute':
            attributes[e] = {}
        elif a == 'has name':
            attributes[e]['name'] = v
        elif a == 'has value':
            attributes[e]['value'] = v
        elif a == 'has attribute':
            entities[e][v] = {}
        else:
            print('What!?')
            print((e, a, v))
    intermediate = {}
    for entity_id, entity in entities.items():
        intermediate[entity_id] = {}
        for attribute_id, empty_attribute_dict in entity.items():
            attribute_dict = attributes.get(attribute_id)
            if attribute_dict:
                intermediate[entity_id][attribute_dict['name']] = attribute_dict['value']
    return condense(intermediate)


def condense(entities):
    refs = []
    for entity_id, entity in entities.items():
        for attr, val in entity.items():
            val_ref = entities.get(val)
            if val_ref:
                refs.append(val)
                entity[attr] = val_ref
    for entity_id, entity in entities.items():
        if entity_id not in refs:
            return entity


demo_data = {
    'dative-url': 'http://127.0.0.1:5678/',
    'old-url': 'http://127.0.0.1:5679/',
    'old-instances': {
        'http://127.0.0.1:5679/bla': {
            'name': 'Blackfoot',
            'url': 'http://127.0.0.1:5679/bla',
            'leader': 'https://projects.linguistics.ubc.ca/blaold',
            'state': 'out-of-sync',
            'auto-sync?': False,
        },
        'http://127.0.0.1:5679/oka': {
            'name': 'Okanagan',
            'url': 'http://127.0.0.1:5679/oka',
            'leader': None,
            'state': None,
            'auto-sync?': False,
        },
        'http://127.0.0.1:5679/sta': {
            'name': "St'at'imcets",
            'url': 'http://127.0.0.1:5679/sta',
            'leader': 'https://projects.linguistics.ubc.ca/staold',
            'state': 'synced',
            'auto-sync?': True,
        },
    },
}

decomposed = decompose(demo_data)
pprint.pprint(decomposed)
assembled = assemble(decomposed)

assert assembled == demo_data
