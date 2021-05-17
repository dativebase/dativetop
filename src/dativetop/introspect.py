"""Code for introspecting the running services. The ``confirm_services_up``
function confirms that all supplied ``utils.Service`` instances supplied are
running and accessible at their URLs.
"""

import logging
import os
import time

import requests
import oldclient as oc

import dativetop.constants as c


logger = logging.getLogger(__name__)


MAX_ATTEMPTS = 3


def normalize_url(service):
    if 'DTServer' == service.name:
        return f'{service.url}/olds'
    if 'OLDService' == service.name:
        return f'{service.url}/root/'
    return service.url


def confirm_services_up(services, attempt_count=1, wait=1):
    failed = []
    for service in services:
        try:
            url = normalize_url(service)
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception as e:
            failed.append(service)
        else:
            logger.info('%s is running at %s', service.name, service.url)
    if failed and attempt_count < MAX_ATTEMPTS:
        time.sleep(wait)
        return confirm_services_up(
            failed,
            attempt_count=attempt_count + 1,
            wait=wait * 2)
    if failed:
        failed_str = ', '.join(f'{s.name} at {s.url}' for s in failed)
        msg = f'Failed to detect the following service(s): {failed_str}.'
        logger.error(msg)
        return None, msg
    return True, None
