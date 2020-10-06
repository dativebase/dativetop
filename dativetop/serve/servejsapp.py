"""DativeTop: Serve JavaScript App

Functionality for serving a JavaScript app locally, in a separate thread, using
a Python server.
"""

from http.server import SimpleHTTPRequestHandler
import logging
import os
import socket
import socketserver
import threading
import urllib.parse


logger = logging.getLogger(__name__)


def _translate_path(path, root):
    """Direct copy of /http/server.py except that ``root`` replaces the call
    to ``os.getcwd()``. This is needed so that we can serve the static files of
    the JS app without calling os.chdir (which would mess up other local servers).
    """
    path = path.split('?', 1)[0]
    path = path.split('#', 1)[0]
    trailing_slash = path.rstrip().endswith('/')
    try:
        path = urllib.parse.unquote(path, errors='surrogatepass')
    except UnicodeDecodeError:
        path = urllib.parse.unquote(path)
    path = os.path.normpath(path)   # was ``path = posixpath.normpath(path)``
    words = path.split(os.path.sep)  # was ``words = path.split('/')``
    words = filter(None, words)
    path = root
    for word in words:
        if os.path.dirname(word) or word in (os.curdir, os.pardir):
            continue
        path = os.path.join(path, word)
    if trailing_slash:
        path += '/'
    return path


def get_custom_http_handler(name, root_path):
    """Return a subclass of ``SimpleHTTPRequestHandler`` that always serves
    paths relative to ``root_path`` instead of using ``os.getcwd()``.
    """

    class CustomHTTPHandler(SimpleHTTPRequestHandler):

        def translate_path(self, path):
            return _translate_path(path, root_path)

        def log_message(self, format, *args):
            """Log message, e.g., to JS App named 'Dative', using the DativeTop
            logger, wrapped as follows::

                ('2019-07-14 12:15:55,397 dativetop.serve.servejsapp       INFO'
                 ' Dative JS App: <MSG>')

            """
            logger.info('%s JS App: ' + format, *((name,) + args))

    return CustomHTTPHandler


def _serve_local_js_app(our_server=None):
    our_server.serve_forever()


class CustomTCPServer(socketserver.TCPServer):
    """This allows us to shutdown the server immediately when the user
    quits DativeTop. This avoids the TIME_WAIT issue. See
    https://stackoverflow.com/questions/6380057/python-binding-socket-address-already-in-use/18858817#18858817
    """

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


def serve_local_js_app(name, ip, port, url, root_path):
    """Serve the local JS app at ip:port in a separate thread.

    Return an argument-less func that, when called, will stop the local server
    and close the thread.
    """
    OurCustomHTTPHandler =  get_custom_http_handler(name, root_path)
    our_server = CustomTCPServer((ip, port), OurCustomHTTPHandler)
    thread = threading.Thread(
        target=_serve_local_js_app,
        kwargs={'our_server': our_server},
        daemon=True)
    thread.start()
    logger.info('{} should be being served at {}'.format(name, url))
    def stop_our_server():
        logger.info('Shutting down %s at %s.', name, url)
        our_server.shutdown()
        our_server.server_close()
        thread.join()
        logger.info('%s at %s should be shut down.', name, url)
    return stop_our_server
