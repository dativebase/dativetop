"""DativeTop: a Toga app that serves Dative and the OLD locally.

DativeTop transforms Dative/OLD into a desktop application using Toga. It
serves the Dative JavaScript/CoffeeScript GUI (SPA) locally and displays it in
a native WebView. It also serves the OLD locally. The local Dative instance can
then be used to interact with the OLD instances being served by the local OLD.

The ultimate goal is to be able to distribute native binaries so that DativeTop
can be easily installed and launched as a desktop application by non-technical
users.
"""

from http.server import SimpleHTTPRequestHandler
import io
import json
import logging
import os
import posixpath
import re
import socket
import socketserver
import subprocess
import sys
import threading
import urllib.parse
import webbrowser

from paste.deploy import appconfig
import pyperclip
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, LEFT, RIGHT


logging.basicConfig(
    filename='dativetop.log',
    level=logging.INFO)


HERE = os.path.dirname(os.path.dirname(__file__))

APP_NAME = 'DativeTop'
APP_ID = 'org.dativebase.dativetop'
ICONS_FILE_NAME = 'OLDIcon.icns'
ICONS_FILE_PATH = os.path.join('icons', ICONS_FILE_NAME)
IP = '127.0.0.1'

DATIVE_WEBSITE_URL = 'http://www.dative.ca/'
DATIVE_PORT = 5678
DATIVE_URL = 'http://{}:{}/'.format(IP, DATIVE_PORT)
DATIVE_ROOT = os.path.join(HERE, 'src', 'dative', 'dist')


OLD_PORT = 5679
OLD_URL = 'http://{}:{}/'.format(IP, OLD_PORT)
OLD_DIR = os.path.join(HERE, 'src', 'old')
OLD_CFG_PTH = os.path.join(OLD_DIR, 'config.ini')
OLD_SETTINGS = appconfig(
    'config:{}'.format(OLD_CFG_PTH), relative_to='.')
OLD_CONFIG = {'__file__': OLD_SETTINGS['__file__'],
              'here': OLD_SETTINGS['here']}
OLD_WEB_SITE_URL = 'http://www.onlinelinguisticdatabase.org/'
DATIVE_WEB_SITE_URL = 'http://www.dative.ca/'

os.environ['OLD_DB_RDBMS'] = 'sqlite'
os.environ['OLD_SESSION_TYPE'] = 'file'


# JavaScript to copy any selected text
COPY_SELECTION_JS = (
    'if (window.getSelection) {\n'
    '  window.getSelection().toString();\n'
    '} else if (document.selection && document.selection.type != "Control") {\n'
    '  document.selection.createRange().text;\n'
    '}')


# JavaScript/jQuery to cut (copy and remove) any selected text
CUT_SELECTION_JS = (
    "var focused = $(':focus');\n"
    "var focused_ntv = focused[0];\n"
    "var start = focused_ntv.selectionStart;\n"
    "var end = focused_ntv.selectionEnd;\n"
    "var focused_val = focused.val();\n"
    "var new_focused_val = focused_val.slice(0, start) + "
    "focused_val.slice(end, focused_val.length);\n"
    "focused.val(new_focused_val);\n"
    "focused_ntv.setSelectionRange(start, start);\n"
    "focused_val.slice(start, end);"
)


# JavaScript/jQuery to select all text
SELECT_ALL_JS = (
    "$(':focus').select();"
)


def paste_js(clipboard):
    """Paste the string ``clipboard`` into the selected text of the focused
    element in the DOM using JavaScript/jQuery.
    """
    return (
        "var focused = $(':focus');\n"
        "var focused_ntv = focused[0];\n"
        "var start = focused_ntv.selectionStart;\n"
        "var end = focused_ntv.selectionEnd;\n"
        "var focused_val = focused.val();\n"
        "focused.val(focused_val.slice(0, start) + "
        "`{}` + focused_val.slice(end, focused_val.length));\n"
        "var cursorPos = start + `{}`.length;\n"
        "focused_ntv.setSelectionRange(cursorPos, cursorPos);"
    ).format(clipboard, clipboard)


def get_dativetop_version():
    version_file_path = os.path.join(HERE, 'dativetop', '__init__.py')
    try:
        with io.open(version_file_path, encoding='utf8') as version_file:
            version_match = re.search(
                r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
            if version_match:
                return version_match.group(1)
            print('Unable to find DativeTop version in {}'.format(
                version_file_path))
            return 'unknown'
    except Exception:
        print('Unable to find DativeTop version in {}'.format(version_file_path))
        return 'unknown'


def get_dative_version():
    dative_pkg_path = os.path.join(DATIVE_ROOT, 'package.json')
    try:
        with io.open(dative_pkg_path) as filei:
            dative_pkj_json = json.load(filei)
        return dative_pkj_json['version']
    except Exception:
        print('Unable to find Dative package.json at {}'.format(dative_pkg_path))
        return 'unknown'


def get_old_version():
    old_info_path = os.path.join(HERE, 'old', 'views', 'info.py')
    old_setup_path = os.path.join(OLD_DIR, 'setup.py')
    if os.path.isfile(old_setup_path):
        try:
            with io.open(old_setup_path, encoding='utf8') as version_file:
                version_match = re.search(
                    r"^VERSION = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
                if version_match:
                    return version_match.group(1)
                else:
                    raise RuntimeError("Unable to find OLD version string.")
        except Exception:
            print('Unable to find OLD setup.py at {}'.format(old_setup_path))
            return 'unknown'
    elif os.path.isfile(old_info_path):
        try:
            with io.open(old_info_path, encoding='utf8') as version_file:
                version_match = re.search(
                    r"^\s*['\"]version['\"]:\s+['\"]([^'\"]*)['\"]", version_file.read(), re.M)
                if version_match:
                    return version_match.group(1)
                else:
                    raise RuntimeError("Unable to find OLD version string.")
        except Exception:
            print('Unable to find OLD info.py at {}'.format(old_info_path))
            return 'unknown'
    else:
        print('Neither of these files exist so unable to get OLD version: {}'
              ' {}'.format(old_setup_path, old_info_path))
        return 'unknown'


def translate_path(path, root):
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


def launch_dativetop(stop_serving_dative, stop_serving_old):
    icon = toga.Icon('icons/OLDIcon.icns')
    app = DativeTop(stop_serving_dative,
                    stop_serving_old,
                    name=APP_NAME,
                    app_id=APP_ID,
                    icon=icon)
    app.main_loop()


def launch_dativetop_new():
    return DativeTop(
        APP_NAME,
        APP_ID,
        icon=ICONS_FILE_PATH)


class DativeTop(toga.App):

    def __init__(self, stop_serving_dative, stop_serving_old, *args, **kwargs):
        self._about_window = None
        self.webview = None
        self.stop_serving_dative = stop_serving_dative
        self.stop_serving_old = stop_serving_old
        super(DativeTop, self).__init__(*args, **kwargs)

    def startup(self):
        self.main_window = toga.MainWindow(
            title=self.name,
            size=(1500, 1000),
            position=(0, 0),
        )
        self.webview = toga.WebView(style=Pack(flex=1))
        self.main_window.content = self.webview
        self.webview.url = DATIVE_URL
        self.set_commands()
        self.main_window.show()

    def get_about_window(self):
        """Return the "About" window: a Toga window with the DativeTop icon and
        the versions of DativeTop, Dative and the OLD displayed.
        TODO: it would be nice if the text could be center-aligned underneath
        the DativeTop icon. Unfortunately, I found it difficult to do this
        using Toga's box model and ``Pack`` layout engine.
        """
        if self._about_window:
            return self._about_window
        dativetop_label = toga.Label('DativeTop {}'.format(
            get_dativetop_version()))
        dative_label = toga.Label('Dative {}'.format(
            get_dative_version()))
        old_label = toga.Label('OLD {}'.format(
            get_old_version()))
        image_from_path = toga.Image('private_resources/icons-originals/OLD-logo.png')
        logo = toga.ImageView(image_from_path)
        logo.style.update(height=72)
        logo.style.update(width=72)
        logo.style.update(direction=COLUMN)
        text_box = toga.Box(
            children=[
                dativetop_label,
                dative_label,
                old_label,
            ]
        )
        text_box.style.update(direction=COLUMN)
        text_box.style.update(alignment=CENTER)
        text_box.style.update(padding_left=20)
        text_box.style.update(padding_top=20)
        outer_box = toga.Box(
            children=[
                logo,
                text_box,
            ]
        )
        outer_box.style.update(direction=COLUMN)
        outer_box.style.update(alignment=CENTER)
        outer_box.style.update(padding=10)
        about_window = toga.Window(
            title=' ',
            id='about DativeTop window',
            minimizable=False,
            # resizeable = False,  # messes up layout
            size=(300, 150),
            position=(500, 200),
        )
        about_window.content = outer_box
        self._about_window = about_window
        return self._about_window

    def about_cmd(self, sender):
        about_window = self.get_about_window()
        about_window.show()

    def copy_cmd(self, sender):
        pyperclip.copy(str(self.webview.evaluate(COPY_SELECTION_JS)))

    def cut_cmd(self, sender):
        pyperclip.copy(str(self.webview.evaluate(CUT_SELECTION_JS)))

    def select_all_cmd(self, sender):
        self.webview.evaluate(SELECT_ALL_JS)

    def paste_cmd(self, sender):
        self.webview.evaluate(paste_js(pyperclip.paste().replace('`', r'\`')))

    def reload_cmd(self, sender):
        self.webview.url = DATIVE_URL

    def back_cmd(self, sender):
        self.webview.evaluate('window.history.back();')

    def forward_cmd(self, sender):
        self.webview.evaluate('window.history.forward();')

    @staticmethod
    def visit_old_web_site_cmd(sender):
        webbrowser.open(OLD_WEB_SITE_URL, new=1, autoraise=True)

    @staticmethod
    def visit_dative_web_site_cmd(sender):
        webbrowser.open(DATIVE_WEB_SITE_URL, new=1, autoraise=True)

    @staticmethod
    def visit_dative_in_browser_cmd(sender):
        webbrowser.open(DATIVE_URL, new=1, autoraise=True)

    @staticmethod
    def visit_old_in_browser_cmd(sender):
        webbrowser.open('{}/old/'.format(OLD_URL), new=1, autoraise=True)

    def quit_cmd(self, sender):
        self.stop_serving_dative()
        self.stop_serving_old()
        self.exit()

    def set_commands(self):
        self.commands = toga.CommandSet(None)

        about_cmd = toga.Command(
            self.about_cmd,
            label='About DativeTop',
            group=toga.Group.APP,
            section=0)

        cut_cmd = toga.Command(
            self.cut_cmd,
            label='Cut',
            shortcut='x',
            group=toga.Group.EDIT,
            section=0)

        copy_cmd = toga.Command(
            self.copy_cmd,
            label='Copy',
            shortcut='c',
            group=toga.Group.EDIT,
            section=0)

        paste_cmd = toga.Command(
            self.paste_cmd,
            label='Paste',
            shortcut='v',
            group=toga.Group.EDIT,
            section=0)

        select_all_cmd = toga.Command(
            self.select_all_cmd,
            label='Select All',
            shortcut='a',
            group=toga.Group.EDIT,
            section=0)

        quit_cmd = toga.Command(
            self.quit_cmd,
            'Quit DativeTop',
            shortcut='q',
            group=toga.Group.APP,
            section=sys.maxsize)

        visit_dative_in_browser_cmd = toga.Command(
            self.visit_dative_in_browser_cmd,
            label='Visit Dative in Browser',
            group=toga.Group.HELP,
            order=0)

        visit_old_in_browser_cmd = toga.Command(
            self.visit_old_in_browser_cmd,
            label='Visit OLD in Browser',
            group=toga.Group.HELP,
            order=1)

        visit_old_web_site_cmd = toga.Command(
            self.visit_old_web_site_cmd,
            label='Visit OLD Web Site',
            group=toga.Group.HELP,
            order=3)

        visit_dative_web_site_cmd = toga.Command(
            self.visit_dative_web_site_cmd,
            label='Visit Dative Web Site',
            group=toga.Group.HELP,
            order=2)

        reload_cmd = toga.Command(
            self.reload_cmd,
            label='Reload DativeTop',
            shortcut='r',
            group=toga.Group.VIEW)

        history_group = toga.Group('History', order=70)

        back_cmd = toga.Command(
            self.back_cmd,
            label='Back',
            shortcut='[',
            group=history_group)

        forward_cmd = toga.Command(
            self.forward_cmd,
            label='Forward',
            shortcut=']',
            group=history_group)

        self.commands.add(
            # DativeTop
            about_cmd,
            quit_cmd,
            # Edit
            cut_cmd,
            copy_cmd,
            paste_cmd,
            select_all_cmd,
            # View
            reload_cmd,
            # History
            back_cmd,
            forward_cmd,
            # Help
            visit_dative_in_browser_cmd,
            visit_old_in_browser_cmd,
            visit_old_web_site_cmd,
            visit_dative_web_site_cmd,
        )


def fork_old_server_process():
    os.chdir(OLD_DIR)
    cmd = [
        #'./../../../python/bin/pserve',  # TODO: this is needed in a built appj...
        'pserve',
        '--reload',
        'config.ini',
        'http_port={}'.format(OLD_PORT),
        'http_host={}'.format(IP),
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def monitor_old_server_process(process=None):
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logging.info(output.decode('utf8').strip())
    rc = process.poll()
    return rc


def serve_old():
    process = fork_old_server_process()
    thread1 = threading.Thread(
            target=monitor_old_server_process, kwargs={'process': process}, daemon=True)
    thread1.start()
    print('The OLD is being served at {}'.format(OLD_URL))
    def stop_serving_old():
        process.terminate()
    return stop_serving_old


class DativeHTTPHandler(SimpleHTTPRequestHandler):
    """This handler always serves paths relative to ``DATIVE_ROOT`` instead of
    using ``os.getcwd()``.
    """

    def translate_path(self, path):
        return translate_path(path, DATIVE_ROOT)


def _serve_dative(dative_server=None):
    dative_server.serve_forever()


class MyTCPServer(socketserver.TCPServer):
    """This allows us to shutdown the Dative server immediately when the user
    quits DativeTop. This avoids the TIME_WAIT issue. See
    https://stackoverflow.com/questions/6380057/python-binding-socket-address-already-in-use/18858817#18858817
    """

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


def serve_dative():
    dative_server = MyTCPServer((IP, DATIVE_PORT), DativeHTTPHandler)
    thread2 = threading.Thread(
        target=_serve_dative, kwargs={'dative_server': dative_server}, daemon=True)
    thread2.start()
    print('Dative is being served at {}'.format(DATIVE_URL))
    def stop_serving_dative():
        dative_server.shutdown()
        dative_server.server_close()
        thread2.join()
    return stop_serving_dative


def real_main():
    stop_serving_dative = serve_dative()
    stop_serving_old = serve_old()
    launch_dativetop(stop_serving_dative, stop_serving_old)


class Converter(toga.App):
    def calculate(self, widget):
        try:
            self.c_input.value = (float(self.f_input.value) - 32.0) * 5.0 / 9.0
        except Exception:
            self.c_input.value = '???'

    def startup(self):
        # Create a main window with a name matching the app
        self.main_window = toga.MainWindow(title=self.name)

        # Create a main content box
        f_box = toga.Box()
        c_box = toga.Box()
        box = toga.Box()

        self.c_input = toga.TextInput(readonly=True)
        self.f_input = toga.TextInput()

        self.c_label = toga.Label('Celsius', style=Pack(text_align=LEFT))
        self.f_label = toga.Label('Fahrenheit', style=Pack(text_align=LEFT))
        self.join_label = toga.Label('Is equivalent to', style=Pack(text_align=RIGHT))

        button = toga.Button('Calculate', on_press=self.calculate)

        f_box.add(self.f_input)
        f_box.add(self.f_label)

        c_box.add(self.join_label)
        c_box.add(self.c_input)
        c_box.add(self.c_label)

        box.add(f_box)
        box.add(c_box)
        box.add(button)

        box.style.update(direction=COLUMN, padding_top=10)
        f_box.style.update(direction=ROW, padding=5)
        c_box.style.update(direction=ROW, padding=5)

        self.c_input.style.update(flex=1)
        self.f_input.style.update(flex=1, padding_left=160)
        self.c_label.style.update(width=100, padding_left=10)
        self.f_label.style.update(width=100, padding_left=10)
        self.join_label.style.update(width=150, padding_right=10)

        button.style.update(padding=15, flex=1)

        # Add the content on the main window
        self.main_window.content = box

        # Show the main window
        self.main_window.show()


def demo_main():
    return Converter('Converter', 'org.pybee.converter')


def main():
    #return demo_main()
    return real_main()
