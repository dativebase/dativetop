"""DativeTop: a Toga app that serves Dative and the OLD locally.

DativeTop transforms Dative/OLD into a desktop application using the Python
Briefcase packaging tool.

DativeTop serves the Dative JavaScript/CoffeeScript GUI (SPA) locally and
displays it in a native WebView. It also serves the OLD locally. The local
Dative instance can then be used to interact with the OLD instances being
served by the local OLD.

DativeTop provides its own interface for managing local OLD instances and
configuring them to sync up with leader OLD instances on the Internet.

The ultimate goal is to be able to distribute native binaries so that DativeTop
can be easily installed and launched as a desktop application by non-technical
users.
"""

from collections import namedtuple
import json
import logging
import os
import pprint
import sys
import threading
import webbrowser

import pyperclip
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT

import dativetop.logging
import dativetop.constants as c
import dativetop.communicate as dtc
from dativetop.getsettings import get_settings
import dativetop.introspect as dti
import dativetop.javascripts as dtjs
import dativetop.serve as dtserve
import dativetop.utils as dtutils


logger = logging.getLogger(__name__)


# TODO: stop doing this: ...
os.environ['OLD_DB_RDBMS'] = 'sqlite'
os.environ['OLD_SESSION_TYPE'] = 'file'


class DativeTopWorking(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return DativeTopWorking()






"""DativeTop: a Toga app that serves Dative and the OLD locally.

DativeTop transforms Dative/OLD into a desktop application using the Python
Briefcase packaging tool.

DativeTop serves the Dative JavaScript/CoffeeScript GUI (SPA) locally and
displays it in a native WebView. It also serves the OLD locally. The local
Dative instance can then be used to interact with the OLD instances being
served by the local OLD.

DativeTop provides its own interface for managing local OLD instances and
configuring them to sync up with leader OLD instances on the Internet.

The ultimate goal is to be able to distribute native binaries so that DativeTop
can be easily installed and launched as a desktop application by non-technical
users.
"""

from collections import namedtuple
import json
import logging
import os
import pprint
import sys
import threading
import webbrowser

import pyperclip
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT

import dativetop.logging
import dativetop.constants as c
import dativetop.communicate as dtc
from dativetop.getsettings import get_settings
import dativetop.introspect as dti
import dativetop.javascripts as dtjs
import dativetop.serve as dtserve
import dativetop.utils as dtutils


logger = logging.getLogger(__name__)


# TODO: stop doing this: ...
os.environ['OLD_DB_RDBMS'] = 'sqlite'
os.environ['OLD_SESSION_TYPE'] = 'file'


def dativetop_on_exit(dativetop_app):
    """If we are exiting because of a fatal error, display an error dialog to
    notify the user of that fact.
    """
    if dativetop_app.fatal_error:
        dativetop_app.main_window.error_dialog(
            'Error', dativetop_app.fatal_error)


def launch_dativetop(service_stoppers):
    icon = toga.Icon('resources/dativetop.icns')
    app = DativeTop(service_stoppers,
                    formal_name=c.APP_FORMAL_NAME,
                    app_name=c.APP_NAME,
                    app_id=c.APP_ID,
                    on_exit=dativetop_on_exit,
                    icon=icon)
    app.main_loop()
    return app


def _verify_services(dativetop_app=None, dativetop_settings=None):
    """Verify that all of the DativeTop services are running as expected. If
    they are not, set a fatal error message and tell DativeTop to shut itself
    down. This should be run in a separate thread so that the DativeTop GUI can
    display ASAP and verification can proceed in parallel.
    """
    #pprint.pprint(dativetop_settings)
    domain_entities, err = dti.introspect(dativetop_settings)
    if err:
        msg = ('Failed to start some DativeTop services. Error: {}. DativeTop'
               ' must shut down now.'.format(err))
        logger.error(msg)
        dativetop_app.fatal_error = msg
        dativetop_app.quit_cmd(None)
        return
    logger.info('got domain_entities:')
    logger.info(domain_entities)
    success, err = dtc.communicate(domain_entities)
    if err:
        logger.warning(
            'Failed to communicate the known local domain entities (e.g.,'
            ' running OLD instances to the DativeTop Server process. Error:'
            ' %s.', err)
    else:
        logger.info('This is what we call success: %s', success)


class DativeTop(toga.App):
    """The DativeTop Toga app

    This is a very minimal native app with standard menus in the menubar and
    two ``toga.WebView`` instances that are responsible for displaying the
    locally served Dative CoffeeScript SPA and the locally served DativeTop
    ClojureScript SPA.
    """

    def __init__(self, service_stoppers, *args, **kwargs):
        self.dativetop_settings = get_settings(config_path=c.CONFIG_PATH)
        self._about_window = None
        self.dative_gui = None
        self.dativetop_gui = None
        self.commands = None
        self.service_stoppers = service_stoppers
        self.fatal_error = None
        super(DativeTop, self).__init__(*args, **kwargs)

    def startup(self):
        """On startup, build the Dative and DativeTop JavaScript
        (WebView-hosted) GUIs and display the DativeTop one.
        """
        self.main_window = toga.MainWindow(
            title=self.name,
            size=(1500, 1000),
            position=(0, 0),
        )
        self.set_commands()
        self.dative_gui = self.get_dative_gui()
        self.dativetop_gui = self.get_dativetop_gui()
        self.main_window.content = self.dativetop_gui
        self.main_window.show()
        self.verify_services()

    def verify_services(self):
        thread = threading.Thread(
            target=_verify_services,
            kwargs={'dativetop_app': self,
                    'dativetop_settings': self.dativetop_settings},
            daemon=True)
        thread.start()

    def get_dative_gui(self):
        dative_gui = toga.WebView(style=Pack(flex=1))
        dative_gui.url = c.DATIVE_URL
        return dative_gui

    def get_dativetop_gui(self):
        dativetop_gui = toga.WebView(style=Pack(flex=1))
        dativetop_gui.url = c.DATIVETOP_GUI_URL
        return dativetop_gui

    def get_about_window(self):
        """Return the "About" native window.

        This is a Toga window with the DativeTop icon and the versions of
        DativeTop, Dative and the OLD displayed.

        TODO: it would be nice if the text could be center-aligned underneath
        the DativeTop icon. Unfortunately, I found it difficult to do this
        using Toga's box model and ``Pack`` layout engine.
        """
        if self._about_window:
            return self._about_window
        dativetop_label = toga.Label('DativeTop {}'.format(
            dtutils.get_dativetop_version()))
        dative_label = toga.Label('Dative {}'.format(
            dtutils.get_dative_version()))
        old_label = toga.Label('OLD {}'.format(
            dtutils.get_old_version()))
        image_from_path = toga.Image(c.OLD_LOGO_PNG_PATH)
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

    async def copy_cmd(self, sender):
        clip = await self.dative_gui.evaluate_javascript(dtjs.COPY_SELECTION_JS)
        return pyperclip.copy(str(clip))

    async def cut_cmd(self, sender):
        clip = await self.dative_gui.evaluate_javascript(dtjs.CUT_SELECTION_JS)
        return pyperclip.copy(str(clip))

    async def select_all_cmd(self, sender):
        await self.dative_gui.evaluate_javascript(dtjs.SELECT_ALL_JS)

    async def reset_dative_app_settings_cmd(self, sender):
        """TODO: this does not seem to work ..."""
        await self.dative_gui.evaluate_javascript(dtjs.DESTROY_DATIVE_APP_SETTINGS)
        self.reload_cmd(sender)

    async def get_dative_app_settings(self):
        """Extract the application settings dictionary from the Dative App.
        """
        app_set = await self.dative_gui.evaluate_javascript(
            dtjs.GET_DATIVE_APP_SETTINGS)
        app_set_str = str(app_set).strip()
        if app_set_str:
            try:
                return json.loads(app_set_str)
            except:
                return {}
        return {}

    async def set_dative_app_settings(self, dative_app_settings_dict):
        """Set the application settings dictionary in the Dative App to a JSON
        string created by serializing ``dative_app_settings_dict``.
        """
        y = self.main_window.content
        self.main_window.content = self.dative_gui
        to_eval = dtjs.SET_DATIVE_APP_SETTINGS.format(
            dative_app_settings=json.dumps(dative_app_settings_dict))
        logger.debug('EVAL THIS!:')
        logger.debug(to_eval)
        x = await self.dative_gui.evaluate_javascript(to_eval)
        logger.debug('ret val:')
        logger.debug(x)
        self.main_window.content = y
        logger.debug('\n\n\nDative app settings now')
        app_settings = await self.really_get_dative_app_settings()['servers']
        logger.debug(pprint.pformat(len(app_settings)))

    async def paste_cmd(self, sender):
        await self.dative_gui.evaluate_javascript(
            dtjs.paste_js(pyperclip.paste().replace('`', r'\`')))

    def reload_cmd(self, sender):
        """This should be the equivalent of a browser refresh of the Dative
        SPA.
        """
        self.dative_gui.url = c.DATIVE_URL

    async def really_get_dative_app_settings(self):
        """Return the Dative application settings (from localStorage in the
        JavaScript process). If they are empty, try to retrieve them after
        display Dative in the WebView.
        """
        dative_app_settings = await self.get_dative_app_settings()
        if not dative_app_settings:
            self.main_window.content = self.dative_gui
            dative_app_settings = await self.get_dative_app_settings()
        return dative_app_settings

    def view_dativetop_gui_cmd(self, sender):
        self.main_window.content = self.dativetop_gui

    def view_dative_gui_cmd(self, sender):
        self.main_window.content = self.dative_gui

    def copy_dative_url_to_clipboard_cmd(self, sender):
        pyperclip.copy(c.DATIVE_URL)

    async def back_cmd(self, sender):
        await self.dative_gui.evaluate_javascript('window.history.back();')

    async def forward_cmd(self, sender):
        await self.dative_gui.evaluate_javascript('window.history.forward();')

    @staticmethod
    def visit_old_web_site_cmd(sender):
        webbrowser.open(c.OLD_WEB_SITE_URL, new=1, autoraise=True)

    @staticmethod
    def visit_dative_web_site_cmd(sender):
        webbrowser.open(c.DATIVE_WEB_SITE_URL, new=1, autoraise=True)

    @staticmethod
    def visit_dative_in_browser_cmd(sender):
        webbrowser.open(c.DATIVE_URL, new=1, autoraise=True)

    @staticmethod
    def visit_old_in_browser_cmd(sender):
        webbrowser.open('{}/old/'.format(c.OLD_URL), new=1, autoraise=True)

    def quit_cmd(self, sender):
        """Handle DativeTop quitting. We stop serving Dative and the OLD
        cleanly so that we can start them up again when DativeTop is launched
        anew.
        """
        stop_services(self.service_stoppers)
        self.exit()

    def set_commands(self):
        """Add several Toga Command instances to the Toga CommandSet in
        ``self.commands``.

        This produces DativeTop's menu items (sometimes with keyboard
        shortcuts) and maps them to methods on this class.
        """
        self.commands = toga.CommandSet(self.factory)

        about_cmd = toga.Command(
            self.about_cmd,
            label='About DativeTop',
            group=toga.Group.APP,
            section=0)

        cut_cmd = toga.Command(
            self.cut_cmd,
            label='Cut',
            shortcut=toga.Key.MOD_1 + 'x',
            group=toga.Group.EDIT,
            section=0)

        copy_cmd = toga.Command(
            self.copy_cmd,
            label='Copy',
            shortcut=toga.Key.MOD_1 + 'c',
            group=toga.Group.EDIT,
            section=0)

        paste_cmd = toga.Command(
            self.paste_cmd,
            label='Paste',
            shortcut=toga.Key.MOD_1 + 'v',
            group=toga.Group.EDIT,
            section=0)

        select_all_cmd = toga.Command(
            self.select_all_cmd,
            label='Select All',
            shortcut=toga.Key.MOD_1 + 'a',
            group=toga.Group.EDIT,
            section=0)

        quit_cmd = toga.Command(
            self.quit_cmd,
            'Quit DativeTop',
            shortcut=toga.Key.MOD_1 + 'q',
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
            shortcut=toga.Key.MOD_1 + 'r',
            group=toga.Group.VIEW)

        reset_cmd = toga.Command(
            self.reset_dative_app_settings_cmd,
            label='Reset Dative',
            shortcut=toga.Key.MOD_1 + 'k',
            group=toga.Group.VIEW)

        view_dativetop_gui_cmd = toga.Command(
            self.view_dativetop_gui_cmd,
            label='DativeTop',
            shortcut=toga.Key.MOD_1 + 't',
            group=toga.Group.VIEW,
            order=2)

        view_dative_gui_cmd = toga.Command(
            self.view_dative_gui_cmd,
            label='Dative',
            shortcut=toga.Key.MOD_1 + 'd',
            group=toga.Group.VIEW,
            order=3)

        history_group = toga.Group('History', order=70)

        back_cmd = toga.Command(
            self.back_cmd,
            label='Back',
            shortcut=toga.Key.MOD_1 + '[',
            group=history_group)

        forward_cmd = toga.Command(
            self.forward_cmd,
            label='Forward',
            shortcut=toga.Key.MOD_1 + ']',
            group=history_group)

        self.commands.add(
            # DativeTop
            about_cmd,
            quit_cmd,
            # Edit
            # cut_cmd,
            # copy_cmd,
            # paste_cmd,
            # select_all_cmd,
            # View
            reload_cmd,
            reset_cmd,
            view_dativetop_gui_cmd,
            view_dative_gui_cmd,
            # History
            back_cmd,
            forward_cmd,
            # Help
            visit_dative_in_browser_cmd,
            visit_old_in_browser_cmd,
            visit_old_web_site_cmd,
            visit_dative_web_site_cmd,
        )
        #self.main_window.toolbar.add(about_cmd, quit_cmd)


Stoppers = namedtuple(
    'Stoppers', 'dative, dativetop_gui, dativetop_server, old')


def start_services():
    return Stoppers(
        dative=dtserve.serve_dative(),
        dativetop_gui=dtserve.serve_dativetop_gui(),
        dativetop_server=dtserve.serve_dativetop_server(),
        old=dtserve.serve_old())


def stop_services(stoppers):
    for stopper in stoppers:
        stopper()


def main():
    launch_dativetop(start_services())


