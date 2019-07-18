"""Code for communicating known OLD instances to the DativeTop Server

- Quad: entity, attribute, value, time
- Appendable: quad, hash, integrated_hash

- instance_to_quads(instance, instance_type):
      Given a namedtuple domain entity ``instance`` of type ``instance_type``
      (a string), return a tuple of quads (4-tuples) that would be sufficient to
      represent that domain entity in the append-only log.

- serialize_appendable(appendable):
      JSON-serialize with newline at end

- aol_to_domain_entities(aol, domain_constructors):
      Given an append-only log ``aol``, return a dict from domain entity types
      (pluralized strings, e.g., 'old-instances') to sets of domain entity
      namedtuples (e.g., ``OLDInstance(slug='oka', ...)``.)

"""

import json
import logging
import pprint

import requests
import dtaoldm.aol as aol_mod
import dtaoldm.domain as domain

import dativetop.constants as c


logger = logging.getLogger(__name__)


def _convert_domain_entities_to_nts(domain_entities):
    """Convert a dict of domain entities to a dict whose values are sets of
    domain entity namedtuples, e.g., OLDInstance. The keys should be
    pluralizations of the domain entity type strings, e.g., 'old-instances'.
    The output should be the same structure as that of
    ``dtaoldm.aol::aol_to_domain_entities``.

    .. note:: Returns a "maybe" 2-tuple.
    """
    ret = {f'{k}s': set() for k in domain.CONSTRUCTORS}
    fodder = []  # domain entities (2-tuples of (D.E., err))
    fodder.append(domain.construct_dative_app(**domain_entities['dative_app']))
    fodder.append(domain.construct_old_service(**domain_entities['old_service']))
    for oi_dict in domain_entities['old_instances']:
        fodder.append(domain.construct_old_instance(**oi_dict))
    errors = list(filter(None, [e for _, e in fodder]))
    if errors:
        return None, ' '.join(errors)
    mapper = {domain.DativeApp: f'{domain.DATIVE_APP_TYPE}s',
              domain.OLDInstance: f'{domain.OLD_INSTANCE_TYPE}s',
              domain.OLDService: f'{domain.OLD_SERVICE_TYPE}s',}
    for de, _ in fodder:
        ret[mapper[type(de)]].add(de)
    return ret, None


def _fetch_aol_from_dt_server():
    """Request the AOL from the DativeTop server. It should be a JSON string
    encoding an array of length-3 arrays (these latter being "appendables")
    """
    try:
        resp = requests.get(c.DATIVETOP_SERVER_URL)
        resp.raise_for_status()
        return resp.json(), None
    except json.decoder.JSONDecodeError:
        msg = 'Failed to parse JSON from DativeTop Server response.'
        logger.exception(msg)
        return None, msg
    except requests.exceptions.RequestException:
        msg = 'Failed to fetch the AOL from DativeTop Server.'
        logger.exception(msg)
        return None, msg


def _get_dt_server_aol():
    aol, err = _fetch_aol_from_dt_server()
    if err:
        return None, err
    try:
        return [aol_mod.Appendable(*appbl_lst) for appbl_lst in aol], None
    except Exception as exc:  # pylint: disable=broad-except
        return None, (f'Failed to convert list of lists from DativeTop Server'
                      f' to list of AOL Appendables. Error: {exc}')


def _get_dt_server_domain_entities():
    dt_server_aol, err = _get_dt_server_aol()
    if err:
        return None, err
    return aol_mod.aol_to_domain_entities(
        dt_server_aol, domain.CONSTRUCTORS), None


def communicate(domain_entities):
    """
        {'dative_app': {'url': ''},
         'old_instances': [{'slug': 'poop', 'url': 'http://127.0.0.1:5679/poop'},
                           {'slug': 'panda', 'url': 'http://127.0.0.1:5679/panda'},
                           {'slug': 'cartoon', 'url': 'http://127.0.0.1:5679/cartoon'}],
         'old_service': {'url': ''}}
    """
    known_domain_entities, err = _convert_domain_entities_to_nts(
        domain_entities)
    if err:
        logger.error(
            'Failed to convert known domain entities to dtaoldm namedtuples.'
            ' Error: %s.', err)
        return None, err
    dts_domain_entities, err = _get_dt_server_domain_entities()
    if err:
        logger.error(
            'Failed to fetch domain entities from DativeTop Server.'
            ' Error: %s.', err)
        return None, err

    logger.info('\nKnown Domain Entities:')
    logger.info(pprint.pformat(known_domain_entities))

    logger.info('\nDativeTop Server Domain Entities:')
    logger.info(pprint.pformat(dts_domain_entities))

    return 'foxes', None
