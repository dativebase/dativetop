#!/usr/bin/env python
"""This project has the following goal:

    Use toga to create a native Mac OS application that runs Dative and the
    OLD. It does the following:
    1. Includes the OLD and its dependencies.
    2. Allows the user to configure multiple OLDs and serve them locally using
       a Python server.
    3. Includes Dative and its dependencies and serves it.
       - font-awesome is not included in Dative, but we want a local copy ...
    4. Creates a WebView instance in which to display Dative.
    5. Uses the toga interface machinery to create a native Senex, i.e., an
       administration system for creating and configuring OLDs and the Dative
       interface.
    6. Bundle it up using pybee Briefcase ...

"""

from colosseum import CSS
from concurrent.futures import ProcessPoolExecutor as Executor
import http.server
import os
import socketserver
import threading
from wsgiref.simple_server import make_server
from paste.deploy import appconfig
import toga

from old import main as oldmain

DATIVE_WEBSITE_URL = 'http://www.dative.ca/'
#DATIVE_IP = 'localhost'
DATIVE_IP = '127.0.0.1'
DATIVE_PORT = 9001
DATIVE_URL = 'http://{}:{}/'.format(DATIVE_IP, DATIVE_PORT)

#OLD_IP = 'localhost'
OLD_IP = '127.0.0.1'
OLD_PORT = 5678

OLD_CFG_PTH = 'src/external/old-pyramid/development.ini'
print(os.listdir('.'))
OLD_SETTINGS = appconfig(
    'config:{}'.format(OLD_CFG_PTH), relative_to='.')
OLD_CONFIG = {
    '__file__': OLD_SETTINGS['__file__'],
    'here': OLD_SETTINGS['here']
}

class DativeToga(toga.App):

    def startup(self):
        # TODO: how to get the screen in a cross-platform way?
        self.screen = toga.platform.NSScreen.mainScreen().visibleFrame
        width = self.screen.size.width * 0.9
        self.main_window = toga.MainWindow(
            self.name, size=(width, self.screen.size.height))
        self.main_window.app = self
        self.webview = toga.WebView(style=CSS(flex=1))
        self.main_window.content = self.webview
        self.webview.url = DATIVE_URL
        self.main_window.show()

    def create_menu(self):
        """Create the main menu."""
        # Dative menu.
        dative_menu_item = toga.MenuItem(self.name)
        dative_menu = toga.Menu(self.name)
        about_menu_item = toga.MenuItem(
            'About ' + self.name,
            on_press=lambda x: self.main_window.info_dialog(
                'Dative', 'Version 0.1.0'))
        quit_menu_item = toga.MenuItem(
            'Quit ' + self.name,
            on_press=lambda x: self.main_window.on_close(),
            key_equivalent='q')
        dative_menu_item.add(dative_menu)
        dative_menu.add(about_menu_item)
        dative_menu.add_separator()
        dative_menu.add(quit_menu_item)
        # Help menu.
        help_menu_item = toga.MenuItem('Help')
        help_menu = toga.Menu('Help')
        website_menu_item = toga.MenuItem(
            'Visit Dative web site', on_press=visit_dative_website)
        help_menu.add(website_menu_item)
        help_menu_item.add(help_menu)
        # Main menu.
        main_menu = toga.Menu('MainMenu')
        main_menu.add(dative_menu_item)
        main_menu.add(help_menu_item)
        self.set_main_menu(main_menu)


def visit_dative_website(menu_item):
    import webbrowser
    webbrowser.open(DATIVE_WEBSITE_URL)


def inspect(t):
    for attr in dir(t):
        val = getattr(t, attr)
        print('{}: {}\n'.format(attr, val))


def launch_dative_toga():
    """Launch the Dative Toga application, which right now is just a webview
    for displaying the Dative JavaScript application.
    """
    icon = toga.Icon('src/Dative/icons/OLDIcon.icns')
    app = DativeToga('Dative', 'ca.dative.dative', icon=icon)
    app.main_loop()


def serve_dative_js():
    """Serve the Dative JavaScript application in a new process. Necessary so
    that ``os.chdir`` will not mess up the current working directory of the
    main thread.
    """
    with Executor(max_workers=1) as exe:
        job = exe.submit(_serve_dative_js)


def _serve_dative_js():
    """Serve the Dative JavaScript application in a separate thread."""
    src_path = os.path.dirname(os.path.dirname(__file__))
    dative_js_root = os.path.join(src_path, 'external', 'dative-js', 'dist')
    os.chdir(dative_js_root)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((DATIVE_IP, DATIVE_PORT), Handler)
    httpd.serve_forever()


def serve_old():
    app = oldmain(OLD_CONFIG, **OLD_SETTINGS)
    server = make_server(OLD_IP, OLD_PORT, app)
    server.serve_forever()


if __name__ == '__main__':
    thread1 = threading.Thread(
        target=serve_old, kwargs={}, daemon=True)
    thread1.start()
    # Serve the Dative JavaScript application a separate thread.
    thread2 = threading.Thread(
        target=serve_dative_js, kwargs={}, daemon=True)
    thread2.start()
    # Launch Dative Toga (native OS application)
    launch_dative_toga()
