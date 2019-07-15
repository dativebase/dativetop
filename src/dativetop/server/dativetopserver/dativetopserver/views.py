import json
import logging
from logging.config import dictConfig
import pprint
import sys

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.view import view_config

import dativetopserver.aol as aol


AOL_PATH = 'aol.txt'


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


def is_valid_old(updated_old):
    print(updated_old)
    return True


def append_to_log(request):
    """Add the sequence of appendables in the request to the append-only log."""
    logger.info('Appending to the AOL')
    try:
        payload = request.json_body
    except Exception as exc:
        logger.exception(
            'Exception raised when attempting to get JSON from the request'
            ' body.')
        request.response.status = 400
        return {'error': 'Bad JSON in request body'}
    if not is_valid_old(payload):
        request.response.status = 400
        return {'error': 'The data provided in the PUT request was not valid.'}
    logger.info('payload')
    logger.info(pprint.pformat(payload))
    return aol.get_aol(AOL_PATH)


def get_append_only_log(request):
    logger.info('Returning the entire AOL')
    return aol.get_aol(AOL_PATH)


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
