"""Register a local OLD instance with a local Dative app.

Example script usage to register an OLD named "myold" with the locally running
Dative app::

    $ DATIVETOP_OLD_PORT=5679 \
          DATIVETOP_DATIVE_SERVERS=src/dative/dist/servers.json \
          DATIVETOP_IP=127.0.0.1 \
          python dativetop/scripts/register-old-with-dative.py create myold

The above will add the following object to the JSON array in the local Dative
app's "servers" JSON config file, which is here specified as
src/dative/dist/servers.json using an environment variable::

    [{"name": "myold",
      "type": "OLD",
      "url": "http://127.0.0.1:5679/myold",}]
"""

import json
import os
import sys


DATIVETOP_IP = os.environ.get('DATIVETOP_IP')
DATIVETOP_OLD_PORT = os.environ.get('DATIVETOP_OLD_PORT')
DATIVETOP_DATIVE_SERVERS = os.environ.get('DATIVETOP_DATIVE_SERVERS')


def _get_dative_servers():
    with open(DATIVETOP_DATIVE_SERVERS) as filei:
        return json.load(filei)


def _write_dative_servers(servers):
    with open(DATIVETOP_DATIVE_SERVERS, 'w') as fileo:
        json.dump(servers, fileo)


def _generate_old_dict(old_name):
    url = 'http://{ip}:{port}/{old_name}'.format(
        ip=DATIVETOP_IP,
        port=DATIVETOP_OLD_PORT,
        old_name=old_name)
    return {'name': old_name,
            'type': 'OLD',
            'url': url,
            'serverCode': None,
            'corpusServerURL': None,
            'website': 'http://www.onlinelinguisticdatabase.org'}


def create(old_name):
    servers = _get_dative_servers()
    old_dict = _generate_old_dict(old_name)
    # TODO: maybe treat the name or the key as a primary key and update if
    # there is a match based on that key.
    if old_dict in servers:
        return
    servers.append(old_dict)
    _write_dative_servers(servers)


def destroy(old_name):
    servers = _get_dative_servers()
    old_dict = _generate_old_dict(old_name)
    if old_dict in servers:
        servers = [s for s in servers if s != old_dict]
        _write_dative_servers(servers)


if __name__ == '__main__':
    subcommand, old_name = sys.argv[1:]
    locals()[subcommand](old_name)
