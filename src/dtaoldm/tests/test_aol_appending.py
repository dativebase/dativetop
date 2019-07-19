"""Tests for appending to an AOL, using real-world-like data
"""

import pprint

import dtaoldm.aol as aol_mod
import dtaoldm.domain as domain
import dtaoldm.utils as u
import tests.utils as utils

OKA_OLD_ID = 'ee07263b-ce9c-401f-9f71-4fa69ef3836b'

OKA_OLD_INSTANCE, _ = domain.construct_old_instance(
    id='ee07263b-ce9c-401f-9f71-4fa69ef3836b',
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
    for quad in aol_mod.instance_to_quads(
            OKA_OLD_INSTANCE, domain.OLD_INSTANCE_TYPE):
        aol_mod.append_to_aol(aol, quad)
    return aol


def diff(init_inst, new_inst):
    init_quads = aol_mod.instance_to_quads(init_inst, domain.OLD_INSTANCE_TYPE)
    new_quads = aol_mod.instance_to_quads(new_inst, domain.OLD_INSTANCE_TYPE)
    diff_quads = []
    for nq in new_quads:
        match = [q for q in init_quads if q.attribute == nq.attribute]
        if match:
            if len(match) > 1:
                print(f'This should never happen: there are {len(match)} quads'
                      f' in the initial instance with attribute'
                      f' {nq.attribute}.')
            else:
                match = match[0]
                if match.value != nq.value:
                    diff_quads.append(nq)
        else:
            diff_quads.append(nq)
    return diff_quads

# No change
# leader:   a => b => c
# follower: a => b => c

# No conflict
# leader:   a => b => c
# follower: a => b => c => d

# Conflict
# leader:   a => b => c => X
# follower: a => b => c => d

# Conflict
# leader:   a => b => c => X => Y
# follower: a => b => c => d

# Conflict
# leader:   a => b => c => X
# follower: a => b => c => d => e

def after_neg_idx(lst, idx):
    return lst[len(lst) - idx:]


def get_new_appendables_in_follower(leader, follower):
    """TODO: return to here
    """
    leader_tip_hash = aol_mod.get_tip_hash(leader)
    if not leader_tip_hash:  # Leader is empty, all of follower is new
        return follower
    leader_seen = []
    follower_seen = []
    for i, (l, f) in enumerate(zip(reversed(leader), reversed(follower))):
        lih = l.integrated_hash
        fih = f.integrated_hash
        if lih == fih:
            return after_neg_idx(follower, i)
        if fih in leader_seen:
            return after_neg_idx(follower, i)
        leader_seen.append(lih)
        for ofih, ofidx in reversed(follower_seen):
            if ofih in leader_seen:
                return after_neg_idx(follower, ofidx)
        follower_seen.append((fih, i))
    return []


def get_hashes(aol):
    return [a.integrated_hash for a in aol]



def merge_aols(leader, follower, conflict_resolution_strategy='abort'):
    print('\nleader hashes:')
    pprint.pprint(get_hashes(leader))

    print('\nfollower hashes:')
    pprint.pprint(get_hashes(follower))

    new_appendables = get_new_appendables_in_follower(leader, follower)
    print('\nNew appendables:')
    pprint.pprint(new_appendables)


def test_aol_appending():
    """Test that ...
    """
    initial_aol = generate_initial_aol()
    print('initial AOL')
    pprint.pprint(initial_aol)

    extracted_domain_entities = aol_mod.aol_to_domain_entities(
        initial_aol, domain.CONSTRUCTORS)
    extracted_old_instance = [
        oi for oi in extracted_domain_entities['old-instances']
        if oi.slug == OKA_OLD_INSTANCE.slug][0]
    new_quads = diff(extracted_old_instance, OKA_OLD_INSTANCE_UPDATED)

    new_aol = initial_aol[:]
    for quad in new_quads:
        aol_mod.append_to_aol(new_aol, quad)
    print('modified AOL')
    pprint.pprint(new_aol)

    merge_aols(initial_aol, new_aol)

