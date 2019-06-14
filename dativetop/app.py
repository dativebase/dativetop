"""DativeTop: a Toga app that serves Dative and the OLD locally.

DativeTop transforms Dative/OLD into a desktop application using Toga. It
serves the Dative JavaScript/CoffeeScript GUI (SPA) locally and displays it in
a native WebView. It also serves the OLD locally. The local Dative instance can
then be used to interact with the OLD instances being served by the local OLD.

The ultimate goal is to be able to distribute native binaries so that DativeTop
can be easily installed and launched as a desktop application by non-technical
users.
"""

import logging
import os
import sys
import webbrowser

import pyperclip
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER

from dativetop.constants import (
    APP_NAME,
    APP_ID,
    DATIVE_URL,
    OLD_URL,
    OLD_WEB_SITE_URL,
    OLD_LOGO_PNG_PATH,
    DATIVE_WEB_SITE_URL,
)
from dativetop.togademo import demo_main
from dativetop.javascripts import (
    COPY_SELECTION_JS,
    CUT_SELECTION_JS,
    SELECT_ALL_JS,
    paste_js,
)
from dativetop.servedative import serve_dative
from dativetop.serveold import serve_old
from dativetop.utils import (
    get_dativetop_version,
    get_dative_version,
    get_old_version,
)


logging.basicConfig(
    filename='dativetop.log',
    level=logging.INFO)


# TODO: stop doing this: ...
os.environ['OLD_DB_RDBMS'] = 'sqlite'
os.environ['OLD_SESSION_TYPE'] = 'file'


def launch_dativetop(stop_serving_dative, stop_serving_old):
    icon = toga.Icon('icons/OLDIcon.icns')
    app = DativeTop(stop_serving_dative,
                    stop_serving_old,
                    name=APP_NAME,
                    app_id=APP_ID,
                    icon=icon)
    app.main_loop()


class DativeTop(toga.App):
    """The DativeTop Toga app

    This is a very minimal native ape with standard menus in the menubar and
    a ``toga.WebView`` that displays the locally served Dative CoffeeScript SPA.
    """

    def __init__(self, stop_serving_dative, stop_serving_old, *args, **kwargs):
        self._about_window = None
        self.webview = None
        # self.main_window = None
        self.commands = None
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
        image_from_path = toga.Image(OLD_LOGO_PNG_PATH)
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
        """This should be the equivalent of a browser refresh of the Dative
        SPA.
        """
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
        """Handle DativeTop quitting. We stop serving Dative and the OLD
        cleanly so that we can start them up again when DativeTop is launched
        anew.
        """
        self.stop_serving_dative()
        self.stop_serving_old()
        self.exit()

    def set_commands(self):
        """Add several Toga Command instances to the Toga CommandSet in
        ``self.commands``.

        This produces DativeTop's menu items (sometimes with keyboard
        shortcuts) and maps them to methods on this class.
        """
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


def real_main():
    stop_serving_dative = serve_dative()
    stop_serving_old = serve_old()
    launch_dativetop(stop_serving_dative, stop_serving_old)


def main():
    # demo_main()
    real_main()
