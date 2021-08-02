"""The SyncManager is a single thread of execution that is responsible for
creating sync-OLD! commands.

The SyncManager performs these steps in a loop:

1. Ask DTServer for all open (un-acknowledged) sync-OLD! Commands.
2. Ask DTServer for all OLDs.
3. Identify all auto-syncing OLDs lacking open commands.
4. Create a sync-OLD! command for each OLD identified in (3).
5. Sleep for a time, then return to (1).
"""

import logging
import pprint
import requests
import threading
import time


logger = logging.getLogger(__name__)


def get_open_sync_old_commands(dtserver):
    try:
        return requests.get(f'{dtserver.url}sync_old_commands').json()
    except Exception as e:
        logger.exception('Failed to fetch sync-OLD! commands')
        return []


def enqueue_sync_old_command(dtserver, old_id):
    try:
        resp = requests.post(
            f'{dtserver.url}sync_old_commands',
            json={'old_id': old_id})
        payload = resp.json()
        status = resp.status_code
        return (payload, status), None
    except Exception as e:
        msg = f'Failed to enqueue a sync-OLD! command for OLD {old_id}'
        logger.exception(msg)
        return None, msg


def get_olds(dtserver):
    try:
        return requests.get(f'{dtserver.url}olds').json()
    except Exception as e:
        logger.exception('Failed to fetch OLDs')
        return []


def sync_manager(dtserver, comm):
    while True:
        try:
            commands = get_open_sync_old_commands(dtserver)
            olds = get_olds(dtserver)
            command_old_ids = [soc['old_id'] for soc in commands]
            olds_needing_commands = [
                old['id'] for old in olds
                if old['is_auto_syncing'] and old['id'] not in command_old_ids]

            for old_id in olds_needing_commands:
                result, error = enqueue_sync_old_command(dtserver, old_id)
                if error:
                    logger.error(error)
                else:
                    cmd, status = result
                    if status == 201:
                        logger.info(f'Enqueued sync-OLD! command for OLD'
                                    f' {cmd["old_id"]}')
                    elif status == 200:
                        logger.info(
                            f'There is already an active sync-OLD! command for'
                            f' OLD {cmd["old_id"]}')
        except Exception as e:
            logger.exception('SyncManager failed when attempting to create new'
                             ' sync-OLD! commands')
        finally:
            if comm.get('exit?'):
                break
            time.sleep(2)


def start_sync_manager(dtserver):
    comm = {}
    thread = threading.Thread(
        target=sync_manager,
        kwargs={'dtserver': dtserver, 'comm': comm},
        daemon=True)
    thread.start()
    return thread, comm
