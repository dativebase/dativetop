"""Append-only Log

Functionality for persisting domain objects as appendables entities in an
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
import pprint

import dtaoldm.utils as u


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


def get_json(data):
    return json.dumps(data)


def parse_json(string):
    return json.loads(string)


def serialize_quad(quad):
    return get_json(quad)


def get_hash(string):
    return hashlib.md5(string.encode('utf8')).hexdigest()


def get_hash_of_quad(quad):
    return get_hash(serialize_quad(quad))


HAS_ATTR = 'has'
LACKS_ATTR = 'lacks'
IS_A_ATTR = 'is-a'

BEING_VAL = 'being'

EXTANT_PRED = (HAS_ATTR, BEING_VAL)
NON_EXISTENT_PRED = (LACKS_ATTR, BEING_VAL)

BEING_PREDS = (EXTANT_PRED, NON_EXISTENT_PRED)


def fiat_entity(entity_id=None):
    """Return a quad that asserts the existence of a new entity."""
    entity_id = entity_id or u.get_uuid()
    return Quad(
        entity=entity_id,
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
    being_quad = fiat_entity(instance.id)
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
        return top_appendable.integrated_hash


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


def aol_to_json(aol):
    return json.dumps(aol)


def list_to_aol(aol_list):
    return [Appendable(Quad(*q), h, ih) for q, h, ih in aol_list]


def json_to_aol(json_aol):
    return list_to_aol(json.loads(json_aol))


# ==============================================================================
# Merge Functionality
# ==============================================================================

def find_changes(target, mergee):
    """Find changes, i.e., the suffix of mergee that is not in target.

    What: return the suffix of mergee that is not in target.
    How: reverse pairwise iteration.
    Logical possibilities:

    1. No change
       target:   a => b => c
       mergee:   a => b => c
       changes:

    2. No conflict, new l
       target:   a => b => c => X
       mergee:   a => b => c
       changes:

    3. No conflict, new f
       target:   a => b => c
       mergee:   a => b => c => d
       changes:              => d

    4. Conflict A, equal new
       target:   a => b => c => X
       mergee:   a => b => c => d
       changes:              => d

    5. Conflict B, more target new
       target:   a => b => c => X => Y
       mergee:   a => b => c => d
       changes:              => d

    6. Conflict C, more mergee new
       target:   a => b => c => X
       mergee:   a => b => c => d => e
       changes:              => d => e

    .. warning:: This should maybe better be a shell out to Git ... but it's fun

    """
    if not target:  # target is empty, all of mergee is new
        return mergee
    target_seen = []  # suffix of target hashes seen
    mergee_seen = []  # suffix of mergee hashes seen (2-tuples with indices)
    for i, (l, f) in enumerate(zip(reversed(target), reversed(mergee))):
        target_hash = l.integrated_hash
        mergee_hash = f.integrated_hash
        if (target_hash == mergee_hash or  # (1, 4)
                mergee_hash in target_seen):  # (3, 6)
            return mergee[len(mergee)-i:]
        target_seen.append(target_hash)
        for oth_foll_hash, oth_foll_idx in reversed(mergee_seen):
            if oth_foll_hash in target_seen:
                return mergee[len(mergee)-oth_foll_idx:] # (2, 5)
        mergee_seen.append((mergee_hash, i))
    return mergee


def get_hashes(aol):
    return [a.integrated_hash for a in aol]


NEED_REBASE_ERR = ('There are changes in the target AOL that are not present'
                   ' in the mergee AOL. Please manually rebase the mergee\'s'
                   ' changes or try again with the "rebase" conflict'
                   ' resolution strategy.')


def merge_aols(target, mergee, conflict_resolution_strategy='abort',
               diff_only=False):
    """Merge AOL ``mergee`` into AOL ``target``.

    :param list target: the AOL that will receive the changes.
    :param list mergee: the AOL that will be merged into target; the AOL that
      provides the changes.
    :param str conflict_resolution_strategy: describes how to handle conflicts.
      If the strategy is 'rebase', we will append the new quads from mergee
      onto target, despite the fact that this will result in hashes for those
      appended quads that differ from their input hashes in ``mergee``.
    :param bool diff_only: If True, we only return the suffix of the merged
      result that ``mergee`` would need to append to itself in order to become
      identical with ``target``; if False, we return the entire modified
      ``target``.
    :returns: Always returns a 2-tuple maybe-type structure.

    .. warning:: TODO: this should return a "patch". That is, instead of just
                 returning an AOL, it should return a 2-tuple where the first
                 element is the AOL and the second element is the hash in the
                 ``mergee`` AOL where the patch should be applied.
    """
    new_from_mergee = find_changes(target, mergee)
    if not new_from_mergee:
        if diff_only:
            return find_changes(mergee, target), None
        return target, None
    new_from_target = find_changes(mergee, target)
    if new_from_target:
        if conflict_resolution_strategy != 'rebase':
            return None, NEED_REBASE_ERR
    ret = target
    if diff_only:
        ret = new_from_target
        if not ret:
            return ret, None
    for appendable in new_from_mergee:
        append_to_aol(ret, appendable.quad)
    return ret, None


def diff(init_inst, new_inst, instance_type):
    """Return the list of quads needed to make ``init_inst`` identical to
    ``new_inst``. Both instances must be of type ``instance_type`` (a string).
    """
    if not isinstance(init_inst, type(new_inst)):
        return None, 'Diff requires that both instances be of the same type.'
    init_quads = instance_to_quads(init_inst, instance_type)
    new_quads = instance_to_quads(new_inst, instance_type)
    diff_quads = []
    for nq in new_quads:
        matches = [q for q in init_quads if q.attribute == nq.attribute]
        if matches:
            match = matches[0]
            if match.value != nq.value:  # updated quad
                diff_quads.append(nq)
        else:  # new quad; should not really be possible given record type (namedtuple)
            diff_quads.append(nq)
    return diff_quads
