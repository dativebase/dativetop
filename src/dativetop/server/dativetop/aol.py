"""Append-only Log: functionality for persisting domain entities as entities in
an append-only log.

"""

from collections import namedtuple
from datetime import datetime
import hashlib
import json
import os
import pprint
from uuid import uuid4

from dativetop.domain import (
    construct_old_instance,
    DOMAIN_ENTITIES_TO_ENTITY_TYPES,
)


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


Quad = namedtuple(
    'Quad', (
        'entity',
        'attribute',
        'value',
        'time'))


def fiat_entity():
    """Return a quad that asserts the existence of a new entity."""
    return Quad(
        entity=get_uuid(),
        attribute='has',
        value='being',
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


def instance_to_quads(instance, instance_type):
    """Given a namedtuple domain entity ``instance``, return a tuple of quads
    (4-tuples) that would be sufficient to represent that domain entity in the
    append-only log.
    """
    being_quad = fiat_entity()
    entity_id = being_quad.entity
    type_quad = fiat_attribute(entity_id, 'is_a', instance_type)
    quads = [being_quad, type_quad]
    for attr in instance._fields:
        quad_attr = attr
        if not quad_attr.startswith('is_'):
            quad_attr = f'has_{quad_attr}'
        quads.append(
            fiat_attribute(entity_id, quad_attr, getattr(instance, attr)))
    return tuple(quads)


Appendable = namedtuple(
    'Appendable', (
        'quad',  # a 4-tuple
        'hash',  # MD5 hash of JSON-serialized quad
        'integrated_hash',  # hash of JSON.SERIALIZE(
                            # (<PREV_APPENDABLE_INTEGRATED_HASH>, <HASH>))
    ))


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
    aol = []
    with open(file_path, 'r') as fh:
        for line in fh:
            aol.append(Appendable(*parse_json(line)))
    return aol

