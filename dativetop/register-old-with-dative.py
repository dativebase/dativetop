"""Register a local OLD instance with a local Dative app.

Example script usage to register an OLD named "myold" with the locally running
Dative app::

    $ python dativetop/scripts/register-old-with-dative.py create myold

The above will add the following object to the JSON array in the local Dative
app's "servers" JSON config file, which is here specified as
src/dative/dist/servers.json using an environment variable::

    [{"name": "myold",
      "type": "OLD",
      "url": "http://127.0.0.1:5679/myold",}]
"""

import json
import sys

from getsettings import get_settings




def get_dative_servers(settings):
    with open(settings['dativetop_dative_servers']) as filei:
        return json.load(filei)


def write_dative_servers(servers, settings):
    with open(settings['dativetop_dative_servers'], 'w') as fileo:
        json.dump(servers, fileo)


def generate_old_dict(old_name, settings):
    url = 'http://{ip}:{port}/{old_name}'.format(
        ip=settings['dativetop_ip'],
        port=settings['dativetop_old_port'],
        old_name=old_name)
    return {'name': old_name,
            'type': 'OLD',
            'url': url,
            'serverCode': None,
            'corpusServerURL': None,
            'website': 'http://www.onlinelinguisticdatabase.org'}


def create(old_name, config_path):
    settings = get_settings(config_path=config_path)
    servers = get_dative_servers(settings)
    old_dict = generate_old_dict(old_name, settings)
    # TODO: maybe treat the name or the key as a primary key and update if
    # there is a match based on that key.
    if old_dict in servers:
        return
    servers.append(old_dict)
    write_dative_servers(servers, settings)


def destroy(old_name, config_path):
    settings = get_settings(config_path=config_path)
    servers = get_dative_servers(settings)
    old_dict = generate_old_dict(old_name, settings)
    if old_dict in servers:
        servers = [s for s in servers if s != old_dict]
        write_dative_servers(servers, settings)


if __name__ == '__main__':
    subcommand, old_name, config_path = sys.argv[1:]
    locals()[subcommand](old_name, config_path)
