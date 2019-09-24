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
        msg = ('Failed to parse JSON from the DativeTop Server response to our'
               ' GET request.')
        logger.exception(msg)
        return None, msg
    except requests.exceptions.RequestException:
        msg = 'Failed to fetch the AOL from DativeTop Server.'
        logger.exception(msg)
        return None, msg


def _fetch_dativetop_server_aol():
    """Fetch the AOL from the DativeTop Server."""
    aol, err = _fetch_aol_from_dt_server()
    if err:
        return None, err
    try:
        return [aol_mod.Appendable(*appbl_lst) for appbl_lst in aol], None
    except Exception as exc:  # pylint: disable=broad-except
        return None, (f'Failed to convert list of lists from DativeTop Server'
                      f' to list of AOL Appendables. Error: {exc}')


def _push_aol_to_dativetop_server(aol):
    """Make a PUT request to the DativeTop server in order to push ``aol`` on to
    the server's AOL.
    """
    try:
        resp = requests.put(c.DATIVETOP_SERVER_URL, json=aol)
        resp.raise_for_status()
        return resp.json(), None
    except json.decoder.JSONDecodeError:
        msg = ('Failed to parse JSON from DativeTop Server response to our PUT'
               ' request.')
        logger.exception(msg)
        return None, msg
    except requests.exceptions.RequestException:
        msg = 'Failed to push our AOL to the DativeTop Server.'
        logger.exception(msg)
        return None, msg


def _calculate_aol_from_domain_entities_dict(domain_entities):
    """Return an AOL encoding the domain entities in the dict
    ``domain_entities``. Expected shape of ``domain_entities`` is a dict from
    strings (pluralized names of domain entities) to sets of named tuples,
    where each named tuple represents a single domain entity::

        {'dative-apps': {DativeApp(url='http://127.0.0.1:5678/')},
         'old-instances': {
             OLDInstance(slug='abc', name='', url='...', leader='',
                         state='not synced', is_auto_syncing=False),
             OLDInstance(slug='def', name='', url='...', leader='',
                         state='not synced', is_auto_syncing=False)},
         'old-services': {OLDService(url='http://127.0.0.1:5679/')}}
    """
    aol = []
    for domain_entity_coll_name, domain_entity_set in domain_entities.items():
        domain_entity_type = domain_entity_coll_name[:-1]
        for domain_entity in domain_entity_set:
            for quad in aol_mod.instance_to_quads(
                    domain_entity, domain_entity_type):
                aol = aol_mod.append_to_aol(aol, quad)
    return aol


def communicate(domain_entities):
    """
    Communicate ``domain_entities`` to the DativeTop Server (DTS). Steps:

    1. Fetch the AOL from the DTS.
    2. a. If the AOL is empty, PUT our domain_entities-as-AOL to the DTS
       b. If the AOL is not empty, then...

          - do nothing (MVP)
          - possibly calculate the patch to update it and PUT that patch

    The ``domain_entities`` argument must be a map with the following keys and
    types of values::

        {'dative_app': {'url': 'http://127.0.0.1:5677'},
         'old_instances': [
             {'slug': 'bla', 'url': 'http://127.0.0.1:5679/bla'},
             {'slug': 'oka', 'url': 'http://127.0.0.1:5679/oka'}],
         'old_service': {'url': 'http://127.0.0.1:5679'}}
    """
    known_domain_entities, err = _convert_domain_entities_to_nts(
        domain_entities)
    if err:
        logger.error(
            'Failed to convert known domain entities to dtaoldm namedtuples.'
            ' Error: %s.', err)
        return None, err

    logger.info('Known Domain Entities:')
    logger.info(pprint.pformat(known_domain_entities))

    dt_server_aol, err = _fetch_dativetop_server_aol()
    if err:
        logger.error(
            'Failed to fetch the AOL from the DativeTop Server.'
            ' Error: %s.', err)
        return None, err

    if dt_server_aol:
        logger.info('The DativeTop Server has been initialized. There is no'
                    ' need for the DativeTop app to communicate its'
                    ' introspected domain entities to the server.')
        dts_domain_entities = aol_mod.aol_to_domain_entities(
            dt_server_aol, domain.CONSTRUCTORS)
        logger.info('DativeTop Server Domain Entities:')
        logger.info(pprint.pformat(dts_domain_entities))
        return 'No operation', None

    fresh_aol = _calculate_aol_from_domain_entities_dict(known_domain_entities)

    logger.info('Known Domain Entities as AOL:')
    logger.info(pprint.pformat(fresh_aol))

    response, err = _push_aol_to_dativetop_server(fresh_aol)
    if err:
        logger.error(
            'Failed to push the AOL of known domain entities to the DativeTop'
            ' Server. Error: %s.', err)
        return None, err

    logger.info('Response from DTS to our PUT request:')
    logger.info(response)

    return 'foxes', None
