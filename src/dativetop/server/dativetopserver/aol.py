"""Append-only Log

Functionality for persisting domain objects as appendable entities in an
append-only log.

An appendable is a 3-tuple consisting of a "quad", that quad's hash, and that
quad's "integrated" hash.

A "quad" is an EAVT 4-tuple of strings consisting of:

    1. an Entity: a UUID string,
    2. an Attribute: a string,
    3. an Value: a string,
    4. an Time: an ISO-8601 string representing a UTC datetime.

"""

from collections import namedtuple
from datetime import datetime
import hashlib
import json
import os
from uuid import uuid4


Quad = namedtuple(
    'Quad', (
        'entity',
        'attribute',
        'value',
        'time'))


Appendable = namedtuple(
    'Appendable', (
        'quad',  # a 4-tuple
        'hash',  # MD5 hash of JSON-serialized quad
        'integrated_hash',  # hash of JSON.SERIALIZE(
                            # (<PREV_APPENDABLE_INTEGRATED_HASH>, <HASH>))
    ))


def get_now():
    return datetime.utcnow()


def get_now_str():
    return get_now().isoformat()


def get_json(thing):
    return json.dumps(thing)


def parse_json(string_thing):
    return json.loads(string_thing)


def serialize_quad(quad):
    return get_json(quad)


def get_hash(string_thing):
    return hashlib.md5(string_thing.encode('utf8')).hexdigest()


def get_hash_of_quad(quad):
    return get_hash(serialize_quad(quad))


def get_uuid():
    return str(uuid4())


HAS_ATTR = 'has'
LACKS_ATTR = 'lacks'
IS_A_ATTR = 'is-a'

BEING_VAL = 'being'

EXTANT_PRED = (HAS_ATTR, BEING_VAL)
NON_EXISTENT_PRED = (LACKS_ATTR, BEING_VAL)

BEING_PREDS = (EXTANT_PRED, NON_EXISTENT_PRED)


def fiat_entity():
    """Return a quad that asserts the existence of a new entity."""
    return Quad(
        entity=get_uuid(),
        attribute=HAS_ATTR,
        value=BEING_VAL,
        time=get_now_str(),)


def fiat_attribute(entity_id, attribute, value):
    """Return a quad that asserts that the entity referenced by ``entity_id``
    has the supplied ``attribute`` with value ``value`` at call time UTC.
    """
    return Quad(
        entity=entity_id,
        attribute=attribute,
        value=value,
        time=get_now_str(),)


def domain_to_aol_attr_convert(quad_attr):
    """Convert an attribute from the domain-level syntax (which should be a
    valid Python name) to the AOL-level syntax.
    """
    if not quad_attr.startswith('is_'):
        quad_attr = f'has_{quad_attr}'
    return quad_attr.replace('_', '-')


def aol_to_domain_attr_convert(quad_attr):
    """Convert an attribute from the AOL-level syntax (which should be more
    human-readable) to the domain-level syntax.
    """
    if quad_attr.startswith('has-'):
        quad_attr = quad_attr[4:]
    return quad_attr.replace('-', '_')


def instance_to_quads(instance, instance_type):
    """Given a namedtuple domain entity ``instance`` of type ``instance_type``
    (a string), return a tuple of quads (4-tuples) that would be sufficient to
    represent that domain entity in the append-only log.
    """
    being_quad = fiat_entity()
    return tuple(
        [being_quad,
         fiat_attribute(being_quad.entity, IS_A_ATTR, instance_type)] +
        [fiat_attribute(being_quad.entity,
                        domain_to_aol_attr_convert(attr),
                        getattr(instance, attr))
         for attr in instance._fields])


def get_tip_hash(aol):
    """Return the (integrated) hash at the tip of the append-only log ``aol``.

    If the log is empty, return ``None``.
    """
    try:
        top_appendable = aol[-1]
    except IndexError:
        return None
    else:
        return Appendable(*top_appendable).integrated_hash


def serialize_appendable(appendable):
    return get_json(appendable) + '\n'


def write_aol_to_file(aol, file_path):
    """Write the entire append-only log ``aol`` to disk at path ``file_path``.
    """
    with open(file_path, 'w') as fh:
        for appendable in aol:
            fh.write(serialize_appendable(appendable))


def get_tip_hash_in_file(file_path):
    """Get the integrated hash of the last line (= EAVT quad) in the
    append-only log at path ``file_path``.
    Note: this is inefficient on large files. Consider doing something similar
    to: https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    """
    with open(file_path, 'r') as fh:
        try:
            return Appendable(
                *parse_json(fh.readlines()[-1])).integrated_hash
        except IndexError:
            return None


def get_new_appendables(aol, tip_hash):
    """Return all appendables in ``aol`` that come after the appendable with
    integrated hash ``tip_hash``.
    """
    if tip_hash is None:
        return aol
    offset = 0
    for i, appendable in enumerate(aol):
        if appendable.integrated_hash == tip_hash:
            offset = i + 1
            break
    return aol[offset:]


def append_aol_to_file(aol, file_path):
    """Write all of the new appendables in the append-only log ``aol`` to the
    file at path ``file_path``.
    """
    with open(file_path, 'a') as fh:
        for appendable in get_new_appendables(
                aol, get_tip_hash_in_file(file_path)):
            fh.write(serialize_appendable(appendable))


def persist_aol(aol, file_path):
    """Write the append-only log ``aol`` to disk at path ``file_path``."""
    if os.path.exists(file_path):
        append_aol_to_file(aol, file_path)
    else:
        write_aol_to_file(aol, file_path)


def append_to_aol(aol, quad):
    """Append EAVT quad ``quad`` to the append-only log ``aol``.

    The AOL consists of Appendable instances, 3-tuples, 1) the EAVT quad, 2)
    the hash of that quad, and 3) the integrated hash of that quad.
    """
    hash_of_quad = get_hash_of_quad(quad)
    top_integrated_hash = get_tip_hash(aol)
    integrated_hash_of_quad = get_hash(
        get_json((top_integrated_hash, hash_of_quad)))
    appendable = Appendable(*(quad, hash_of_quad, integrated_hash_of_quad))
    aol.append(appendable)
    return aol


def get_aol(file_path):
    """Read the append-only-log stored on disk at ``file_path`` to a list of
    Appendable instances.
    """
    if not os.path.isfile(file_path):
        persist_aol([], file_path)
    aol = []
    with open(file_path, 'r') as fh:
        for line in fh:
            aol.append(Appendable(*parse_json(line)))
    return aol


def aol_to_domain_entities(aol, domain_constructors):
    """Given an append-only log ``aol``, return a dict from domain entity types
    (pluralized strings, e.g., 'old-instances') to sets of domain entity
    namedtuples (e.g., ``OLDInstance(slug='oka', ...)``.)
    """
    ret = {f'{k}s': set() for k in domain_constructors}
    entities = {}
    for appendable in aol:
        quad = appendable.quad
        e, a, v, _ = quad
        entities.setdefault(e, {})
        if (a, v) in BEING_PREDS:
            if a == HAS_ATTR:
                entities[e]['_extant'] = True
            else:
                entities[e]['_extant'] = False
        elif a == IS_A_ATTR:
            entities[e]['_type'] = v
        else:
            a = aol_to_domain_attr_convert(a)
            entities[e][a] = v
    for dom_ent_dict in entities.values():
        if not dom_ent_dict.get('_extant'):
            continue
        entity_type = dom_ent_dict.get('_type')
        constructor = domain_constructors.get(entity_type)
        if not constructor:
            continue
        domain_entity, err = constructor(**dom_ent_dict)
        if err:
            continue
        key = f'{entity_type}s'
        ret[key].add(domain_entity)
    return ret
