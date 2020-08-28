"""DativeTop: Serve a Pyramid app

Functionality for serving a Pyramid web service locally, in a new
process, using the pserve Python server.
"""

import logging
import os
import shlex
import subprocess
import threading


logger = logging.getLogger(__name__)

def _fork_server_process(ip, port, root_path, config='config.ini'):
    """Use Pyramid's pserve executable to serve the Pyramid app in a new
    process.
    """
    os.chdir(root_path)
    cmd = shlex.split(
        f'pserve'
        f' --reload'
        f' {config}'
        f' http_port={port}'
        f' http_host={ip}')
    # FIXME: this is still needed in a built (e.g., DativeTop.app) app...
    # './../../../python/bin/pserve'
    return subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)


def _monitor_server_process(process=None, name=None):
    """Log at INFO level the stdout of the pserve process that is serving the
    OLD.
    """
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logger.info('%s: %s', name, output.decode('utf8').strip())
    rc = process.poll()
    return rc


def serve_pyr(name, ip, port, url, root_path, config='config.ini'):
    """Serve the Pyramid app locally in a separate thread that forks a
    subprocess that invokes the pserve executable. Return a function that stops
    serving the Pyramid app.
    """
    process = _fork_server_process(ip, port, root_path, config=config)
    thread = threading.Thread(
        target=_monitor_server_process,
        kwargs={'process': process, 'name': name,},
        daemon=True)
    thread.start()
    logger.info('%s should be being served at %s', name, url)
    def stop_serving():
        logger.info('Shutting down %s at %s.', name, url)
        process.terminate()
        logger.info('%s at %s should be shut down.', name, url)
    return stop_serving
