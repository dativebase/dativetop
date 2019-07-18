"""Code for introspecting the running services:

    - Check that Dative GUI, DativeTop GUI, DativeTop Server and OLD Service
      are all running.
    - Return a list of OLD Instances that we can log in to.
"""

import logging
import os
import time

import requests
import oldclient as oc

import dativetop.constants as c


logger = logging.getLogger(__name__)


DEFAULT_URLS = (('Dative', c.DATIVE_URL),
                ('DativeTop GUI', c.DATIVETOP_GUI_URL),
                ('DativeTop Server', c.DATIVETOP_SERVER_URL),
                # OLD needs a subpath under /
                ('OLD Service', f'{c.OLD_URL}root/'),)

MAX_ATTEMPTS = 3


def _find_possible_old_instance_names(dativetop_settings):
    """Return a list of OLD instance dicts, deduced by inspecting the
    .sqlite files listed under ``config['old_db_dirpath']``. Aside from the
    defaults, the file system data gives us the name and local URL of each
    instance.
    """
    old_instances = []
    old_db_dirpath = dativetop_settings.get('old_db_dirpath')
    if old_db_dirpath and os.path.isdir(old_db_dirpath):
        for e_name in os.listdir(old_db_dirpath):
            e_path = os.path.join(old_db_dirpath, e_name)
            if os.path.isfile(e_path):
                old_name, ext = os.path.splitext(e_name)
                if ext == '.sqlite':
                    old_instances.append(
                        {'local_path': e_path,
                         'db_file_name': old_name,
                         'url': f'{c.OLD_URL}{old_name}',})
    return old_instances


def _determine_running_old_instances(dativetop_settings):
    """Return a list of dicts representing the OLD instances that are actually
    running locally.

    .. warning:: We accomplish this verification by logging into each OLD
                 serially. Aside from the possible performance issue of serial
                 HTTP requests, this skirts the issue that some OLD instances
                 might have modified credentials. Credential management must be
                 dealt with.
    """
    ret = []
    username = dativetop_settings['dflt_old_username']
    password = dativetop_settings['dflt_old_password']
    hidden_password = '*' * len(password)
    for oi_dict in _find_possible_old_instance_names(
            dativetop_settings):
        url = oi_dict['url']
        old_client = oc.OLDClient(url)
        can_login = old_client.login(username, password)
        if not can_login:
            logger.warning(
                'Cannot login to local OLD at %s using username %s and password'
                ' %s.', url, username, hidden_password)
            continue
        ret.append({'url': oi_dict['url'],
                    'slug': oi_dict['db_file_name'],})
    return ret


def _get_domain_entities(dativetop_settings):
    """Return a dict describing the DativeTop domain entities. This is
    information that will need to be communicated to the DativeTop Server.
    """
    return {
        'dative_app': {'url': c.DATIVE_URL},
        'old_service': {'url': c.OLD_URL},
        'old_instances': _determine_running_old_instances(dativetop_settings)}


def _confirm_all_services_up(attempt_count=1, wait=1, urls=None):
    urls = urls or DEFAULT_URLS
    failed = []
    for name, url in urls:
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except:
            logger.warning('%s is not yet running at %s.', name, url)
            failed.append((name, url))
        else:
            logger.info('%s is running at %s', name, url)
    if failed and attempt_count < MAX_ATTEMPTS:
        time.sleep(wait)
        return _confirm_all_services_up(
            attempt_count=attempt_count + 1,
            wait=wait * 2,
            urls=failed)
    if failed:
        failed_str = ', '.join('{0} at {1}'.format(*s) for s in failed)
        return None, f'Failed to detect the following service(s): {failed_str}.'
    return True, None


def introspect(dativetop_settings):
    """Confirm that we can reach each of the local services. Return a dict of
    domain entities; this should be information about the local DativeApp,
    OLDService and OLDInstances that can be communicated to the DativeTop
    Server service.
    """
    _, err = _confirm_all_services_up()
    if err:
        logger.error(err)
        return None, err
    logger.info('All DativeTop services are running locally!')
    return _get_domain_entities(dativetop_settings), None
