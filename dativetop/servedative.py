"""DativeTop: Serve Dative

Functionality for serving the Dative CoffeeScript SPA locally, in a separate
thread, using a Python server.
"""

from http.server import SimpleHTTPRequestHandler
import os
import posixpath  # TODO: issues when DativeTop is running on Windows? ...
import socket
import socketserver
import threading
import urllib.parse

from dativetop.constants import (
    IP,
    DATIVE_PORT,
    DATIVE_URL,
    DATIVE_ROOT,
)


def _translate_path(path, root):
    """Direct copy of /http/server.py except that ``root`` replaces the call
    to ``os.getcwd()``. This is needed so that we can serve the static files of
    Dative without calling os.chdir (which would mess up serving the OLD).
    """
    path = path.split('?', 1)[0]
    path = path.split('#', 1)[0]
    trailing_slash = path.rstrip().endswith('/')
    try:
        path = urllib.parse.unquote(path, errors='surrogatepass')
    except UnicodeDecodeError:
        path = urllib.parse.unquote(path)
    path = posixpath.normpath(path)
    words = path.split('/')
    words = filter(None, words)
    path = root
    for word in words:
        if os.path.dirname(word) or word in (os.curdir, os.pardir):
            continue
        path = os.path.join(path, word)
    if trailing_slash:
        path += '/'
    return path


class DativeHTTPHandler(SimpleHTTPRequestHandler):
    """This handler always serves paths relative to ``DATIVE_ROOT`` instead of
    using ``os.getcwd()``.
    """

    def translate_path(self, path):
        return _translate_path(path, DATIVE_ROOT)


def _serve_dative(dative_server=None):
    dative_server.serve_forever()


class DativeTCPServer(socketserver.TCPServer):
    """This allows us to shutdown the Dative server immediately when the user
    quits DativeTop. This avoids the TIME_WAIT issue. See
    https://stackoverflow.com/questions/6380057/python-binding-socket-address-already-in-use/18858817#18858817
    """

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


def serve_dative():
    """Serve the Dative SPA at localhost in a separate thread.

    Return an argument-less func that, when called, will stop the Dative server
    and close the thread.
    """
    dative_server = DativeTCPServer((IP, DATIVE_PORT), DativeHTTPHandler)
    thread = threading.Thread(
        target=_serve_dative, kwargs={'dative_server': dative_server}, daemon=True)
    thread.start()
    print('Dative is being served at {}'.format(DATIVE_URL))
    def stop_serving_dative():
        dative_server.shutdown()
        dative_server.server_close()
        thread.join()
    return stop_serving_dative
