"""DativeTop: Serve DativeTop Server, a Pyramid web service

Functionality for serving the DativeTop Server Pyramid web service locally, in
a new process.
"""

import logging
import os
import re
import shlex
import subprocess
import threading

from dativetop.constants import (
    IP,
    DATIVETOP_SERVER_PORT,
    DATIVETOP_SERVER_DIR,
    DATIVETOP_SERVER_URL,
)


def _fork_dativetop_server_process():
    """Shell out to Python to serve the DativeTop server in a new process."""
    dativetop_app_path = os.path.join(DATIVETOP_SERVER_DIR, 'app.py')
    cmd = shlex.split(
        f'python'
        f' {dativetop_app_path}'
        f' {IP}'
        f' {DATIVETOP_SERVER_PORT}')
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def _monitor_dativetop_server_process(process=None):
    """Log at INFO level the stdout of the Python process that is serving the
    DativeTop Server.
    """
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logging.info(output.decode('utf8').strip())
    rc = process.poll()
    return rc


def serve_dativetop_server():
    """Serve the OLD locally in a separate thread that forks a subprocess that
    invokes the pserve executable. Return a function that stops serving the OLD.
    """
    process = _fork_dativetop_server_process()
    thread = threading.Thread(
        target=_monitor_dativetop_server_process,
        kwargs={'process': process},
        daemon=True)
    thread.start()
    print('The DativeTop Server is being served at {}'.format(
        DATIVETOP_SERVER_URL))
    def stop_serving_dativetop_server():
        process.terminate()
    return stop_serving_dativetop_server
