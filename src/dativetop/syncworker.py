"""The SyncWorker is a single thread of execution that is responsible for
executing sync-OLD! commands.

The SyncWorker performs these steps in a loop:

1. Using DTServer, pop the next sync-OLD! command off of the queue.
2. Determine whether the OLD already exists and create it if it does not.
3. Fetch the last modified values for each resource in the local OLD.
4. Fetch the last modified values for each resource in the remote OLD.
5. Compute a diff in order to determine required updates, deletes and adds.
6. Fetch the remote resources that have been updated or added.
7. Mutate the local OLD's SQLite db so that it matches the remote leader.
8. Sleep for a time and then return to (1).
"""

import datetime
import json
import logging
import os
import shlex
import shutil
import subprocess
import threading
import time

from oldclient import OLDClient
import requests
import sqlalchemy as sqla

import dativetop.constants as c


logger = logging.getLogger(__name__)


DEFAULT_LOCAL_OLD_USERNAME = 'admin'
DEFAULT_LOCAL_OLD_PASSWORD = 'adminA_1'


def parse_datetime_string(datetime_string):
    return datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S.%f')


def parse_date_string(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()


def prepare_value_for_upsert(table_name, k, v):
    if 'datetime_' in k and v:
        try:
            return parse_datetime_string(v)
        except Exception as e:
            logger.warning(
                'Failed to parse value "%s" as datetime in table %s, column %s.',
                v, table_name, k)
            raise e
    if 'date_' in k and v:
        try:
            return parse_date_string(v)
        except Exception as e:
            logger.warning(
                'Failed to parse value "%s" as date in table %s, column %s.',
                v, table_name, k)
            raise e
    return v


def prepare_row_for_upsert(table_name, row):
    row = {k: prepare_value_for_upsert(table_name, k, v)
           for k, v in row.items()}
    if table_name == 'user':
        del row['password']
        del row['salt']
    return row


def pop_sync_old_command(dtserver):
    try:
        response = requests.put(f'{dtserver.url}sync_old_commands')
        if response.status_code == 404:
            logger.debug('No sync-OLD! messages currently on the queue')
            return None
        if response.status_code == 200:
            return response.json()
        logger.error(
            'Received an unexpected response code %s when attempting to pop'
            ' the next sync-OLD! command.', response.status_code)
        return None
    except Exception:
        msg = 'Failed to pop the next sync-OLD! command from DTServer'
        logger.exception(msg)
        return None


def complete_sync_old_command(dtserver, command):
    try:
        response = requests.delete(
            f'{dtserver.url}sync_old_commands/{command["id"]}')
        if response.status_code == 404:
            logger.warning(
                f'Failed to complete command {command["id"]}: it does not'
                f' exist.')
            return None
        if response.status_code == 200:
            return response.json()
        logger.error(
            'Received an unexpected response code %s when attempting to'
            ' complete sync-OLD! command %s.',
            response.status_code,
            command['id'])
        return None
    except Exception:
        msg = f'Failed to complete sync-OLD! command {command["id"]}.'
        logger.exception(msg)
        return None


def handle_command(command, old_service):
    """
    1. identify the OLD from the command
    {'acked': True,
     'id': 'cbcfb97d-6f72-4851-997d-173560c6173d',
     'old_id': 'd9d5563d-a29a-46b3-85f2-6a3a1104f7fa'}
    """
    return None


def fetch_old(dtserver, old_id):
    try:
        return requests.get(f'{dtserver.url}olds/{old_id}').json()
    except Exception:
        logger.exception('Failed to fetch OLD %s', old_id)
        return None


def old_store_dir_exists(old):
    old_store_dir = os.path.join(c.OLD_DIR, 'store', old['slug'])
    return os.path.isdir(old_store_dir)


def can_authenticate_to_old(old):
    old_client = OLDClient(old['url'])
    try:
        return old_client.login(
            DEFAULT_LOCAL_OLD_USERNAME,
            DEFAULT_LOCAL_OLD_PASSWORD)
    except Exception as e:
        logger.warning(
            f'Exception of type {type(e)} when attempting to'
            f' authenticate to the OLD')
        return False


def authenticate_to_leader(old):
    logger.debug(
        f'checking if we can login to the leader OLD at {old["leader"]}'
        f' using username {old["username"]} and password'
        f' {old["password"]}')
    old_client = OLDClient(old['leader'])
    try:
        logged_in = old_client.login(old['username'], old['password'])
        if logged_in:
            return old_client
        return False
    except Exception:
        logger.exception(f'Failed to login to the leader OLD {old["leader"]}')
        return False


def does_old_exist(old):
    dir_exists = old_store_dir_exists(old)
    if dir_exists:
        can_auth = can_authenticate_to_old(old)
        if can_auth:
            return True
    return False


def get_dative_servers(path):
    with open(path) as filei:
        return json.load(filei)


def write_dative_servers(servers, path):
    with open(path, 'w') as fileo:
        json.dump(servers, fileo)


def generate_old_dict(old):
    return {'name': old['name'],
            'type': 'OLD',
            'url': old['url'],
            'serverCode': None,
            'corpusServerURL': None,
            'website': 'http://www.onlinelinguisticdatabase.org'}


def register_old_with_dative(old):
    try:
        servers_path = os.path.join(c.DATIVE_ROOT, 'servers.json')
        servers = get_dative_servers(servers_path)
        old_dict = generate_old_dict(old)
        if old_dict in servers:
            return True
        servers.append(old_dict)
        write_dative_servers(servers, servers_path)
        return True
    except Exception:
        logger.warning(f'Failed to register OLD {old["slug"]} with Dative')
        return False


def unregister_old_with_dative(old):
    servers_path = os.path.join(c.DATIVE_ROOT, 'servers.json')
    servers = get_dative_servers(servers_path)
    old_dict = generate_old_dict(old)
    if old_dict in servers:
        servers = [s for s in servers if s != old_dict]
        write_dative_servers(servers, servers_path)


def create_local_old(old):
    os.chdir(c.OLD_DIR)
    initialize_old_path = 'initialize_old'
    if not shutil.which(initialize_old_path):
        initialize_old_path = os.path.join(
            os.path.dirname(c.HERE),
            'app_packages',
            'bin',
            'initialize_old')
    cmd = initialize_old_path + f' configlocal.ini {old["slug"]}'
    logger.info(f'Running command `{cmd}` to create the {old["slug"]} OLD')
    cmd = shlex.split(cmd)
    child = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    stdout_data, stderr_data = child.communicate()
    if child.returncode != 0:
        logger.warning(f'Failed to create new local OLD {old["slug"]}')
        try:
            logger.warning(stdout_data)
            logger.warning(stderr_data)
        except Exception:
            logger.warning('Failed to log stdout and stderr')
        return False
    logger.info(f'Successfully issued the command to create the new local OLD'
                f' {old["slug"]}')
    old_exists = does_old_exist(old)
    if not old_exists:
        logger.warning(f'Failed to create new local OLD {old["slug"]}')
        return False
    logger.info(f'Confirmed that the new local OLD {old["slug"]} exists')
    is_registered = register_old_with_dative(old)
    if not is_registered:
        logger.warning(f'Failed to register local OLD {old["slug"]} with Dative')
        return False
    logger.info(f'Registered local OLD {old["slug"]} with Dative')
    logger.info(f'Created new local OLD {old["slug"]}')
    return True


class SyncOLDError(Exception):
    pass


def get_diff(prev, curr):
    diff = {'delete': {}, 'add': {}, 'update': {}}
    for table, ids in prev.items():
        for id_, modified in ids.items():
            if id_ not in curr[table]:
                diff['delete'].setdefault(table, []).append(int(id_))
            elif modified != curr[table][id_]:
                diff['update'].setdefault(table, []).append(int(id_))
    for table, ids in curr.items():
        for id_, modified in ids.items():
            if id_ not in prev[table]:
                diff['add'].setdefault(table, []).append(int(id_))
    return diff


def batch_tables(tables, batch_size=200):
    """Given a ``tables`` map from table names (strings) to lists of table row
    IDs (integers), return a list of maps of the same form such that every list
    of row IDs contains ``batch_size`` or fewer elements."""
    batches = []
    while tables:
        new_remainder = {}
        batch = {}
        for table_name, ids in tables.items():
            if not ids:
                continue
            batch[table_name] = ids[:batch_size]
            remainder_ids = ids[batch_size:]
            if remainder_ids:
                new_remainder[table_name] = remainder_ids
        batches.append(batch)
        tables = new_remainder
    return batches


def process_command(dtserver, old_service, command):
    """Process a sync-OLD! command."""

    # Get the OLD metadata from DTServer
    old = fetch_old(dtserver, command['old_id'])
    old['url'] = f'{old_service.url}/{old["slug"]}'

    # Determine whether the OLD already exists and create it if necessary
    old_exists = does_old_exist(old)
    if not old_exists:
        old_exists = create_local_old(old)
        if not old_exists:
            msg = f'Failed to create the OLD {old["slug"]} locally'
            logger.warning(msg)
            raise SyncOLDError(msg)

    # Abort if we are not set to sync or if there is nothing to sync with
    if not old['is_auto_syncing']:
        logger.debug(f'OLD {old["slug"]} is not set to auto-sync')
        return
    if not old['leader']:
        logger.debug(f'OLD {old["slug"]} has no remote leader OLD')
        return
    leader_client = authenticate_to_leader(old)
    if not leader_client:
        logger.warning(f'Unable to login to leader OLD {old["leader"]}')
        return

    # Fetch the last modified values for each resource in the local OLD and in
    # the leader OLD and construct a diff.
    local_client = OLDClient(old['url'])
    local_client.login(
        DEFAULT_LOCAL_OLD_USERNAME,
        DEFAULT_LOCAL_OLD_PASSWORD)
    local_last_mod = local_client.get('sync/last_modified')
    leader_last_mod = leader_client.get('sync/last_modified')
    diff = get_diff(local_last_mod, leader_last_mod)

    # Perform the local updates by modifying the SQLite db of the OLD directly.
    meta = sqla.MetaData()
    db_path = os.path.join(c.OLD_DIR, f"{old['slug']}.sqlite")
    engine = sqla.create_engine(f'sqlite:///{db_path}')
    with engine.connect() as conn:
        # Perform any deletions
        delete_state = diff['delete']
        if delete_state:
            for table_name, rows in delete_state.items():
                if not rows:
                    continue
                table = sqla.Table(table_name, meta, autoload_with=engine)
                conn.execute(
                    table.delete().where(
                        table.c.id.in_(rows)))
        # Perform any additions
        add_params = diff['add']
        if add_params:
            for batch in batch_tables(add_params):
                add_state = leader_client.post(
                    'sync/tables', {'tables': batch})
                for table_name, rows in add_state.items():
                    if not rows:
                        continue
                    table = sqla.Table(table_name, meta, autoload_with=engine)
                    conn.execute(
                        table.insert(),
                        [prepare_row_for_upsert(table_name, row)
                        for row in rows.values()])
        # Perform any updates
        update_params = diff['update']
        if update_params:
            for batch in batch_tables(update_params):
                update_state = leader_client.post(
                    'sync/tables', {'tables': batch})
                for table_name, rows in update_state.items():
                    if not rows:
                        continue
                    table = sqla.Table(table_name, meta, autoload_with=engine)
                    for row in rows.values():
                        row_id = row['id']
                        updated_row = prepare_row_for_upsert(table_name, row)
                        conn.execute(
                            table.update().where(
                                table.c.id == row_id).values(**updated_row))


def sync_worker(dtserver, old_service):
    while True:
        try:
            # Pop and then process the next sync-OLD! command
            command = pop_sync_old_command(dtserver)
            if not command:
                continue
            process_command(dtserver, old_service, command)
        except SyncOLDError as e:
            logger.exception(str(e))
        except Exception as e:
            logger.exception(
                'Unexpected exception during SyncWorker\'s attempt to process'
                ' the next sync-OLD! command')
        finally:
            # Tell DTServer that we have finished processing the command.
            if command:
                complete_sync_old_command(dtserver, command)
            time.sleep(5)


def start_sync_worker(dtserver, old_service):
    thread = threading.Thread(
        target=sync_worker,
        kwargs={'dtserver': dtserver,
                'old_service': old_service},
        daemon=True)
    thread.start()
