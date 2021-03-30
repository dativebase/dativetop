import json
import logging
from logging.config import dictConfig
import pprint
import sys
from urllib.parse import urlparse

from wsgiref.simple_server import make_server
from pyramid.config import Configurator

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


def validate_old_service_url(url):
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
    updated_old_service = m.update_old_service(url.rstrip('/'))
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
    return {'error': 'The old_service only recognizes GET and PUT requests.'}

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
