"""DativeTop: Serve OLD

Functionality for serving the OLD Pyramid web service locally, in a new
process, using the pserve Python server.
"""

import logging
import os
import re
import shlex
import subprocess
import threading

from dativetop.constants import (
    IP,
    OLD_PORT,
    OLD_URL,
    OLD_DIR,
)


def _fork_old_server_process():
    """Use Pyramid's pserve executable to serve the OLD in a new process."""
    os.chdir(OLD_DIR)
    cmd = shlex.split(
        f'pserve'
        f' --reload'
        f' config.ini'
        f' http_port={OLD_PORT}'
        f' http_host={IP}')
    # FIXME: this is still needed in a built (e.g., DativeTop.app) app...
    # './../../../python/bin/pserve'
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def _monitor_old_server_process(process=None):
    """Log at INFO level the stdout of the pserve process that is serving the
    OLD.
    """
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logging.info(output.decode('utf8').strip())
    rc = process.poll()
    return rc


def serve_old():
    """Serve the OLD locally in a separate thread that forks a subprocess that
    invokes the pserve executable. Return a function that stops serving the OLD.
    """
    process = _fork_old_server_process()
    thread = threading.Thread(
        target=_monitor_old_server_process,
        kwargs={'process': process},
        daemon=True)
    thread.start()
    print('The OLD is being served at {}'.format(OLD_URL))
    def stop_serving_old():
        process.terminate()
    return stop_serving_old
