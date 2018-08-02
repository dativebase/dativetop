from concurrent.futures import ProcessPoolExecutor as Executor
import http.server
import os
import socketserver
import sys
import threading

from paste.deploy import appconfig
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from wsgiref.simple_server import make_server

from old import main as old_main


HERE = os.path.dirname(os.path.dirname(__file__))

APP_NAME = 'DativeTop'
APP_ID = 'org.dativebase.dativetop'
IP = '127.0.0.1'

DATIVE_WEBSITE_URL = 'http://www.dative.ca/'
DATIVE_PORT = 5678
DATIVE_URL = 'http://{}:{}/'.format(IP, DATIVE_PORT)

OLD_PORT = 5679
OLD_URL = 'http://{}:{}/'.format(IP, OLD_PORT)
OLD_DIR = os.path.join(HERE, 'src', 'old')
OLD_CFG_PTH = os.path.join(OLD_DIR, 'config.ini')
OLD_SETTINGS = appconfig(
    'config:{}'.format(OLD_CFG_PTH), relative_to='.')
OLD_CONFIG = {'__file__': OLD_SETTINGS['__file__'],
              'here': OLD_SETTINGS['here']}


def launch_dativetop():
    """Launch the Dative Toga application, which right now is just a webview
    for displaying the Dative JavaScript application.
    """
    icon = toga.Icon('icons/OLDIcon.icns')
    app = DativeTop(name=APP_NAME,
                    app_id=APP_ID,
                    icon=icon)
    app.main_loop()


class DativeTop(toga.App):

    def startup(self):
        self.main_window = toga.MainWindow(
            title=self.name,
            size=(1500, 1000),
            position=(0, 0),
        )
        self.webview = toga.WebView(style=Pack(flex=1))
        self.main_window.content = self.webview
        self.webview.url = DATIVE_URL
        self.main_window.show()


def _serve_old():
    os.chdir(OLD_DIR)
    app = old_main(OLD_CONFIG, **OLD_SETTINGS)
    server = make_server(IP, OLD_PORT, app)
    server.serve_forever()


def serve_old():
    thread1 = threading.Thread(
        target=_serve_old, kwargs={}, daemon=True)
    thread1.start()
    print('The OLD is being served at {}'.format(OLD_URL))


def _serve_dative_worker():
    """Serve the Dative JavaScript application in a separate thread."""
    dative_root = os.path.join(HERE, 'src', 'dative', 'dist')
    os.chdir(dative_root)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((IP, DATIVE_PORT), Handler)
    httpd.serve_forever()


def _serve_dative():
    """Serve the Dative JavaScript application in a new process. Necessary so
    that ``os.chdir`` will not mess up the current working directory of the
    main thread.
    """
    with Executor(max_workers=1) as exe:
        job = exe.submit(_serve_dative_worker)


def serve_dative():
    thread2 = threading.Thread(
        target=_serve_dative, kwargs={}, daemon=True)
    thread2.start()
    print('Dative is being served at {}'.format(DATIVE_URL))


def main():
    serve_dative()
    serve_old()
    launch_dativetop()

