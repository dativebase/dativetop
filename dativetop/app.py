from http.server import SimpleHTTPRequestHandler
import io
import json
import os
import posixpath
import pyperclip
import re
import socketserver
import sys
import threading
import urllib.parse
import webbrowser
from wsgiref.simple_server import make_server

from paste.deploy import appconfig
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT, BOLD
from toga_cocoa.libs import NSDocumentController, NSOpenPanel, NSMutableArray

from old import main as old_main

HERE = os.path.dirname(os.path.dirname(__file__))

APP_NAME = 'DativeTop'
APP_ID = 'org.dativebase.dativetop'
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


COPY_SELECTION_JS = (
    'if (window.getSelection) {\n'
    '  window.getSelection().toString();\n'
    '} else if (document.selection && document.selection.type != "Control") {\n'
    '  document.selection.createRange().text;\n'
    '}')


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


SELECT_ALL_JS = (
    "$(':focus').select();"
)


def paste_js(clipboard):
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
    with io.open(version_file_path, encoding='utf8') as version_file:
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
        if version_match:
            return version_match.group(1)
        else:
            raise RuntimeError("Unable to find DativeTop version string.")


# TODO: these version getters do NOT work on build DativeTops because the
# source files are in different locations.


def get_dative_version():
    dative_pkg_path = os.path.join(DATIVE_ROOT, 'package.json')
    with io.open(dative_pkg_path) as filei:
        dative_pkj_json = json.load(filei)
    return dative_pkj_json['version']


def get_old_version():
    old_setup_path = os.path.join(OLD_DIR, 'setup.py')
    with io.open(old_setup_path, encoding='utf8') as version_file:
        version_match = re.search(
            r"^VERSION = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
        if version_match:
            return version_match.group(1)
        else:
            raise RuntimeError("Unable to find OLD version string.")


def translate_path(path, root):
    """Direct copy of /http/server.py except that ``root`` replaces the call
    to ``os.getcwd()``.
    """
    path = path.split('?',1)[0]
    path = path.split('#',1)[0]
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

    def __init__(self, *args, **kwargs):
        self._about_window = None
        self.webview = None
        super(DativeTop, self).__init__(*args, **kwargs)

    def startup(self):
        self.main_window = toga.MainWindow(
            title=self.name,
            size=(1500, 1000),
            position=(0, 0),
        )
        self.webview = toga.WebView(style=Pack(flex=1))

        #print('webview native...')
        #print(self.webview._impl.native)
        #print('\n'.join(dir(self.webview._impl)))

        self.main_window.content = self.webview
        self.webview.url = DATIVE_URL
        self.set_commands()
        self.main_window.show()

    def about_cmd(self, sender):
        about_window = self.get_about_window()
        about_window.show()

    def open_file_cmd(self, sender):
        print('open file dialog')
        # from toga_cocoa import NSDocumentController, NSOpenPanel
        panel = NSOpenPanel.openPanel()
        #self.main_window.open_file_dialog('Open a fricking file')
        toga.Window().open_file_dialog('a fricking file')

        """
        print('=' * 80)
        print('NSOpenPanel')
        print(NSOpenPanel)
        print(type(NSOpenPanel))
        for x in dir(NSOpenPanel):
            if not x.startswith('_'):
                print(x)
                print(getattr(NSOpenPanel, x))
                print('\n')
        print('=' * 80)

        print('=' * 80)
        print('panel')
        print(panel)
        print(type(panel))
        for x in dir(panel):
            if not x.startswith('_'):
                print(x)
                print(getattr(panel, x))
                print('\n')
        print('=' * 80)

        fileTypes = NSMutableArray.alloc().init()

        print('self._impl')
        print(self._impl)
        print(type(self._impl))
        print(dir(self._impl))
        print(dir(self._impl.native))

        #self._impl.application_openFiles_(None, panel.URLs)
        import pydoc
        xhelp = pydoc.render_doc(self._impl.application_openFiles_)
        print(xhelp)


        for filetype in self._impl.document_types:
            fileTypes.addObject(filetype)
        NSDocumentController.sharedDocumentController.runModalOpenPanel(
            panel, forTypes=fileTypes)
        print("Untitled File opened?", panel.URLs)
        self.application_openFiles_(None, panel.URLs)
        """




    def get_about_window(self):
        """Return the "About" window: a Toga window with the DativeTop icon and
        the versions of DativeTop, Dative and the OLD displayed.
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

    def copy_cmd(self, sender):
        pyperclip.copy(str(self.webview.evaluate(COPY_SELECTION_JS)))

    def cut_cmd(self, sender):
        pyperclip.copy(str(self.webview.evaluate(CUT_SELECTION_JS)))

    def select_all_cmd(self, sender):
        self.webview.evaluate(SELECT_ALL_JS)

    def paste_cmd(self, sender):
        self.webview.evaluate(paste_js(pyperclip.paste().replace('`', '\`')))

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

    def quit_cmd(self, sender):
        self.exit()

    def set_commands(self):
        self.commands = toga.CommandSet(None)

        about_cmd = toga.Command(
            self.about_cmd,
            label='About DativeTop',
            group=toga.Group.APP,
            section=0)

        open_file_cmd = toga.Command(
            self.open_file_cmd,
            label='Open',
            shortcut='o',
            group=toga.Group.FILE,
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

        visit_old_web_site_cmd = toga.Command(
            self.visit_old_web_site_cmd,
            label='Visit OLD Web Site',
            group=toga.Group.HELP)

        visit_dative_web_site_cmd = toga.Command(
            self.visit_dative_web_site_cmd,
            label='Visit Dative Web Site',
            group=toga.Group.HELP)

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
            # File
            open_file_cmd,
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
            visit_old_web_site_cmd,
            visit_dative_web_site_cmd,
        )


def _serve_old():
    os.chdir(OLD_DIR)

    """
    app = old_main(OLD_CONFIG, **OLD_SETTINGS)
    server = make_server(IP, OLD_PORT, app)
    server.serve_forever()
    """

    import subprocess
    cmd = [
        'pserve',
        '--reload',
        'config.ini',
        'http_port={}'.format(OLD_PORT),
        'http_host={}'.format(IP),
    ]
    subprocess.check_output(cmd)



def serve_old():
    thread1 = threading.Thread(
        target=_serve_old, kwargs={}, daemon=True)
    thread1.start()
    print('The OLD is being served at {}'.format(OLD_URL))


class DativeHTTPHandler(SimpleHTTPRequestHandler):
    """This handler always serves paths relative to ``DATIVE_ROOT`` instead of
    using ``os.getcwd()``.
    """

    def translate_path(self, path):
        return translate_path(path, DATIVE_ROOT)


def _serve_dative():
    Handler = DativeHTTPHandler
    httpd = socketserver.TCPServer((IP, DATIVE_PORT), Handler)
    httpd.serve_forever()


def serve_dative():
    thread2 = threading.Thread(
        target=_serve_dative, kwargs={}, daemon=True)
    thread2.start()
    print('Dative is being served at {}'.format(DATIVE_URL))


def main():
    serve_dative()
    serve_old()
    launch_dativetop()
