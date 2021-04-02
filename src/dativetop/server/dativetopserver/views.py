import json
import logging
from logging.config import dictConfig
import sys
from urllib.parse import urlparse

from pyramid.config import Configurator
from sqlalchemy.orm.exc import NoResultFound
from wsgiref.simple_server import make_server

import dativetopserver.models as m

logging_config = dict(
    version=1,
    formatters={
        'f': {'format':
              '%(asctime)s %(name)-32s %(levelname)-8s %(message)s'}
    },
    handlers={
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
    },
    root={
        'handlers': ['h'],
        'level': logging.DEBUG,
    },
)

dictConfig(logging_config)


logger = logging.getLogger(__name__)


def append_to_log(request):
    """Add the sequence of appendables in the request to the append-only
    log.
    """
    logger.info('Appending to the AOL')
    try:
        payload = request.json_body
    except json.decoder.JSONDecodeError:
        logger.exception(
            'Exception raised when attempting to get JSON from the request'
            ' body.')
        request.response.status = 400
        return {'error': 'Bad JSON in request body'}

    logger.info('DativeTop Server: received this payload of type %s in'
                ' append_to_log.', type(payload))
    try:
        mergee = aol_mod.list_to_aol(payload)
    except Exception as err:
        logger.warning('Exception when calling ``mergee = aol_mod.list_to_aol(payload)``')
        logger.warning(err)
        raise

    logger.info('Got mergee AOL')
    target = aol_mod.get_aol(AOL_PATH)
    logger.info('Got target AOL')
    merged, err = aol_mod.merge_aols(
        target, mergee, conflict_resolution_strategy='rebase')
    if err:
        logger.warning('Failed to merge mergee into target')
        request.response.status = 400
        return {'error': err}
    logger.info('Merged mergee into target')
    aol_mod.persist_aol(merged, AOL_PATH)
    logger.info('Persisted mergee into target')
    # What we want to return here is the AOL that the sender does not know
    # about ... the patch. See ongoing work at dtaoldm/aol.py.
    return []


def get_append_only_log(request):
    logger.info('MONKEYS!')
    tip_hash = request.GET.get('head')
    logger.info('Returning the AOL after hash %s', tip_hash)
    aol = aol_mod.get_aol(AOL_PATH)
    ret = aol_mod.get_new_appendables(aol, tip_hash)
    logger.info('Returning AOL suffix of %s elements', len(ret))
    return ret


def append_only_log(request):
    """Handle all requests. There is only one endpoint, the AOL root endoint at
    /. Only 2 HTTP methods are accepted: PUT and GET. PUT is for appending, GET
    is for reading.
    """
    if request.method == 'PUT':
        return append_to_log(request)
    if request.method == 'GET':
        return get_append_only_log(request)
    request.response.status = 405
    return {'error': 'Only GET and PUT requests are permitted.'}


def validate_local_url(url):
    parsed = urlparse(url.rstrip('/'))
    if not parsed.port:
        return 'no port'
    allowed_hostnames = ['localhost', '127.0.0.1']
    if parsed.hostname not in allowed_hostnames:
        return 'hostname invalid; only {} are permitted'.format(
            ', '.join(allowed_hostnames))
    if parsed.scheme != 'http':
        return 'scheme is not http'
    if parsed.path:
        return 'path is not empty'
    if parsed.params:
        return 'params is not empty'
    if parsed.query:
        return 'query is not empty'
    if parsed.fragment:
        return 'fragment is not empty'

# /old_service endpoint

validate_old_service_url = validate_local_url

def update_old_service(request):
    """Update the (URL of the) OLD Service."""
    logger.info('Updating the OLD Service')
    try:
        payload = request.json_body
    except json.decoder.JSONDecodeError:
        logger.exception(
            'Exception raised when attempting to get JSON from the request'
            ' body.')
        request.response.status = 400
        return {'error': 'Bad JSON in request body'}
    logger.info('DativeTop Server: received payload of type %s in'
                ' PUT /old_service.', type(payload))
    url = None
    if isinstance(payload, dict):
        url = payload.get('url')
    if url is None:
        request.response.status = 400
        return {'error': 'No OLD service URL in request body'}
    if not isinstance(url, str):
        request.response.status = 400
        return {'error': 'URL must be a string'}
    validation_error = validate_old_service_url(url)
    if validation_error:
        request.response.status = 400
        return {'error': validation_error}
    url = url.rstrip('/')
    dative_app_url = m.get_dative_app().url.rstrip('/')
    if url == dative_app_url:
        return {'error': 'OLD Service URL must be different from Dative App URL'}
    updated_old_service = m.update_old_service(url)
    return m.serialize_old_service(updated_old_service)


def get_old_service(request):
    logger.info('Getting the OLD Service')
    return m.serialize_old_service(m.get_old_service())


def old_service(request):
    if request.method == 'PUT':
        return update_old_service(request)
    if request.method == 'GET':
        return get_old_service(request)
    request.response.status = 405
    return {'error': ('The /old_service endpoint only recognizes GET and PUT'
                      ' requests.')}

# /dative_app endpoint

validate_dative_app_url = validate_local_url

def update_dative_app(request):
    """Update the (URL of the) Dative App."""
    logger.info('Updating the Dative App')
    try:
        payload = request.json_body
    except json.decoder.JSONDecodeError:
        logger.exception(
            'Exception raised when attempting to get JSON from the request'
            ' body.')
        request.response.status = 400
        return {'error': 'Bad JSON in request body'}
    logger.info('DativeTop Server: received payload of type %s in'
                ' PUT /dative_app.', type(payload))
    url = None
    if isinstance(payload, dict):
        url = payload.get('url')
    if url is None:
        request.response.status = 400
        return {'error': 'No Dative app URL in request body'}
    if not isinstance(url, str):
        request.response.status = 400
        return {'error': 'URL must be a string'}
    validation_error = validate_dative_app_url(url)
    if validation_error:
        request.response.status = 400
        return {'error': validation_error}
    url = url.rstrip('/')
    old_service_url = m.get_old_service().url.rstrip('/')
    if url == old_service_url:
        return {'error': 'Dative App URL must be different from OLD Service URL'}
    updated_dative_app = m.update_dative_app(url)
    return m.serialize_dative_app(updated_dative_app)


def get_dative_app(request):
    logger.info('Getting the Dative App')
    return m.serialize_dative_app(m.get_dative_app())


def dative_app(request):
    if request.method == 'PUT':
        return update_dative_app(request)
    if request.method == 'GET':
        return get_dative_app(request)
    request.response.status = 405
    return {'error': ('The /dative_app endpoint only recognizes GET and PUT'
                      ' requests.')}


def get_json_payload(request):
    try:
        return request.json_body, None
    except json.decoder.JSONDecodeError:
        logger.exception(
            'Exception raised when attempting to get JSON from the request'
            ' body.')
        request.response.status = 400
        return None, {'error': 'Bad JSON in request body'}


def str_or_none(val):
    if val is None:
        return val
    if isinstance(val, str):
        return val
    raise m.DTValueError('value must be a string')


def boolean(val):
    if isinstance(val, bool):
        return val
    raise m.DTValueError('value must be a boolean')


def create_old(request):
    payload, error = get_json_payload(request)
    if error:
        return error
    slug = payload.get('slug')
    if not slug:
        return {'error': 'slug is required'}
    try:
        old = m.create_old(
            slug,
            name=str_or_none(payload.get('name')),
            leader=str_or_none(payload.get('leader')),
            username=str_or_none(payload.get('username')),
            password=str_or_none(payload.get('password')),
            is_auto_syncing=boolean(payload.get('is_auto_syncing', False)))
    except m.DTValueError as e:
        request.response.status = 400
        return {'error': str(e)}
    except Exception:
        request.response.status = 500
        return {'error': 'Internal server error'}
    request.response.status = 201
    return m.serialize_old(old)


# Read OLDS (DTGUI)
# WARNING: no pagination
def read_olds(request):
    return [m.serialize_old(old) for old in m.get_olds()]


def read_old(request):
    old_id = request.matchdict['old_id']
    try:
        old = m.get_old(old_id)
    except NoResultFound:
        request.response.status = 404
        return {'error': 'No OLD with supplied ID'}
    return m.serialize_old(old)


def update_old(request):
    old_id = request.matchdict['old_id']
    try:
        old = m.get_old(old_id)
    except NoResultFound:
        request.response.status = 404
        return {'error': 'No OLD with supplied ID'}
    payload, error = get_json_payload(request)
    if error:
        return error
    # Cannot update slug (for now, too complicated)
    try:
        payload = {
            'name': str_or_none(payload.get('name', old.name)),
            'leader': str_or_none(payload.get('leader', old.leader)),
            'username': str_or_none(payload.get('username', old.username)),
            'password': str_or_none(payload.get('password', old.password)),
            'is_auto_syncing': boolean(payload.get('is_auto_syncing',
                                                   old.is_auto_syncing))}
        if payload == {attr:getattr(old, attr) for attr in payload}:
            updated_old = old
        else:
            updated_old = m.update_old(old, **payload)
    except m.DTValueError as e:
        request.response.status = 400
        return {'error': str(e)}
    except Exception:
        request.response.status = 500
        return {'error': 'Internal server error'}
    request.response.status = 200
    return m.serialize_old(updated_old)


def validate_old_state(old_state):
    if old_state is None:
        return None, 'state must be supplied'
    try:
        return getattr(m.old_state, old_state), None
    except (AttributeError, TypeError):
        return None, 'state must be one of {}'.format(
            ', '.join(m.old_state._asdict().keys()))


def validate_state_transition(old_state, new_state):
    if new_state in m.old_state_transitions[old_state]:
        return new_state, None
    return None, 'illegal state transition'


def transition_old_state(request):
    old_id = request.matchdict['old_id']
    try:
        old = m.get_old(old_id)
    except NoResultFound:
        request.response.status = 404
        return {'error': 'No OLD with supplied ID'}
    payload, error = get_json_payload(request)
    if error:
        return error
    try:
        new_state, error = validate_old_state(payload.get('state'))
        if error:
            return {'error': error}
        if new_state == old.state:
            updated_old = old
        else:
            new_state, error = validate_state_transition(old.state, new_state)
            if error:
                return {'error': error}
            updated_old = m.update_old(old, state=new_state)
    except m.DTValueError as e:
        request.response.status = 400
        return {'error': str(e)}
    except Exception:
        request.response.status = 500
        return {'error': 'Internal server error'}
    request.response.status = 200
    return m.serialize_old(updated_old)


def delete_old(request):
    old_id = request.matchdict['old_id']
    try:
        old = m.get_old(old_id)
    except NoResultFound:
        request.response.status = 404
        return {'error': 'No OLD with supplied ID'}
    deleted_old = m.delete_old(old)
    return deleted_old


# /olds endpoint
def olds(request):
    if request.method == 'POST':
        return create_old(request)
    if request.method == 'GET':
        return read_olds(request)
    request.response.status = 405
    return {'error': ('The /olds endpoint only recognizes GET and POST'
                      ' requests.')}


# /olds/{old_id} endpoint
def old(request):
    if request.method == 'GET':
        return read_old(request)
    if request.method == 'PUT':
        return update_old(request)
    # TODO: this implies work to delete the OLD.
    if request.method == 'DELETE':
        return delete_old(request)
    request.response.status = 405
    return {'error': ('The /olds/{old_id} endpoint only recognizes GET, PUT and'
                      ' DELETE requests.')}


# /olds/{old_id}/state endpoint
def old_state(request):
    if request.method == 'PUT':
        return transition_old_state(request)
    request.response.status = 405
    return {'error': ('The /olds/{old_id}/state endpoint only recognizes PUT'
                      ' requests.')}


# OLDSyncCommand API:
# Enqueue:  POST   /sync_old_commands
# Pop:      PUT    /sync_old_commands
# Read:     GET    /sync_old_commands/{id}
# Complete: DELETE /sync_old_commands/{id}

def enqueue_command(request):
    payload, error = get_json_payload(request)
    if error:
        return error
    old_id = payload.get('old_id')
    if not old_id:
        request.response.status = 400
        return {'error': 'OLD ID is required'}
    try:
        old = m.get_old(old_id)
    except NoResultFound:
        request.response.status = 404
        return {'error': 'No OLD with supplied ID'}
    return m.serialize_sync_old_command(m.enqueue_sync_old_command(old_id))


def pop_command(request):
    command = m.pop_sync_old_command()
    if not command:
        request.response.status = 404
        return {'error': 'No commands on the queue'}
    return m.serialize_sync_old_command(command)


def read_command(request):
    command_id = request.matchdict['command_id']
    try:
        command = m.get_sync_old_command(command_id)
    except NoResultFound:
        request.response.status = 404
        return {'error': 'No command with supplied ID'}
    return m.serialize_sync_old_command(command)


def complete_command(request):
    command_id = request.matchdict['command_id']
    try:
        command = m.complete_sync_old_command(command_id)
    except NoResultFound:
        request.response.status = 404
        return {'error': 'No acked command with supplied ID'}
    return m.serialize_sync_old_command(command)


def sync_old_commands(request):
    if request.method == 'POST':
        return enqueue_command(request)
    if request.method == 'PUT':
        return pop_command(request)
    request.response.status = 405
    return {'error': ('The /sync_old_commands endpoint only recognizes POST'
                      ' and PUT requests.')}


def sync_old_command(request):
    if request.method == 'GET':
        return read_command(request)
    if request.method == 'DELETE':
        return complete_command(request)
    request.response.status = 405
    return {'error': ('The /sync_old_command/{id} endpoint only recognizes GET'
                      ' and DELETE requests.')}


def get_ip_port():
    args = sys.argv
    ip = '127.0.0.1'
    port = 6543
    if len(args) == 2:
        port = args[1]
    elif len(args) > 2:
        ip, port = args[1:3]
    return ip, int(port)


def main(ip, port):
    config = Configurator()
    config.include('cors')
    config.add_cors_preflight_handler()

    config.add_route('old-service', '/old_service')
    config.add_view(old_service,
                    route_name='old-service',
                    renderer='json')

    config.add_route('dative-app', '/dative_app')
    config.add_view(dative_app,
                    route_name='dative-app',
                    renderer='json')

    config.add_route('old_state', '/olds/{old_id}/state')
    config.add_view(old_state,
                    route_name='old_state',
                    renderer='json')

    config.add_route('old', '/olds/{old_id}')
    config.add_view(old,
                    route_name='old',
                    renderer='json')

    config.add_route('olds', '/olds')
    config.add_view(olds,
                    route_name='olds',
                    renderer='json')

    config.add_route('sync_old_command', '/sync_old_commands/{command_id}')
    config.add_view(sync_old_command,
                    route_name='sync_old_command',
                    renderer='json')

    config.add_route('sync_old_commands', '/sync_old_commands')
    config.add_view(sync_old_commands,
                    route_name='sync_old_commands',
                    renderer='json')

    config.add_route('append-only-log', '/')
    config.add_view(append_only_log,
                    route_name='append-only-log',
                    renderer='json')

    app = config.make_wsgi_app()
    logger.info(f'Serving at http://{ip}:{port}/')
    server = make_server(ip, port, app)
    server.serve_forever()


if __name__ == '__main__':
    ip, port = get_ip_port()
    main(ip, port)
