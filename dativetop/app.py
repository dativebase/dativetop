"""DativeTop: a Toga app that serves Dative and the OLD locally.

DativeTop transforms Dative/OLD into a desktop application using Toga. It
serves the Dative JavaScript/CoffeeScript GUI (SPA) locally and displays it in
a native WebView. It also serves the OLD locally. The local Dative instance can
then be used to interact with the OLD instances being served by the local OLD.

The ultimate goal is to be able to distribute native binaries so that DativeTop
can be easily installed and launched as a desktop application by non-technical
users.
"""

import json
import logging
import os
import pprint
import shlex
import sys
import subprocess
import time
from uuid import uuid4
import webbrowser

import pyperclip
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT

from dativetop.constants import (
    APP_NAME,
    APP_ID,
    CONFIG_PATH,
    DATIVE_URL,
    OLD_URL,
    OLD_WEB_SITE_URL,
    OLD_LOGO_PNG_PATH,
    DATIVE_WEB_SITE_URL,
)
from dativetop.getsettings import get_settings
from dativetop.togademo import demo_main
from dativetop.javascripts import (
    COPY_SELECTION_JS,
    CUT_SELECTION_JS,
    DESTROY_DATIVE_APP_SETTINGS,
    GET_DATIVE_APP_SETTINGS,
    SET_DATIVE_APP_SETTINGS,
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


OLD_INSTANCES_TABLE_HEADINGS = (
    'Name',
    'URL',
    'Size',
)

def get_size_of_old_instance(old_instance_dict):
    sqlite_path = old_instance_dict['local_path']
    logging.info('get size of OLD at %s.', sqlite_path)
    sqlite_file_size = os.path.getsize(sqlite_path)
    logging.info('OLD SQLite file %s has size %s in bytes.', sqlite_path,
                 sqlite_file_size)
    dir_path = os.path.join(
        os.path.dirname(os.path.dirname(sqlite_path)),
        os.path.splitext(os.path.basename(sqlite_path))[0])
    dir_size = os.path.getsize(dir_path)
    logging.info('OLD directory %s has size %s in bytes.', dir_path, dir_size)
    # /Users/joeldunham/Development/dativetop/dativetop/oldinstances/dbs/myold.sqlite
    return sqlite_file_size + dir_size

def launch_dativetop(stop_serving_dative, stop_serving_old):
    icon = toga.Icon('icons/OLDIcon.icns')
    app = DativeTop(stop_serving_dative,
                    stop_serving_old,
                    name=APP_NAME,
                    app_id=APP_ID,
                    icon=icon)
    app.main_loop()


def generate_uuid():
    return str(uuid4())



def copy_old_instance_url(table_obj, row=None):
    try:
        pyperclip.copy(row.url)
    except Exception as exc:
        logging.warning(
            'Failed to copy the selected OLD instance table row URL to the'
            ' clipboard. Error: %s (%s).', exc, type(exc))


def log_old_instances(msg, old_instances, include_paths=False):
    lines = [msg]
    for o in old_instances:
        name = o.get('name', 'Unknown name')
        url = o['url']
        path = o.get('local_path', 'Unknown path')
        lines.append('- Name: {}'.format(name))
        lines.append('  URL: {}'.format(url))
        if include_paths:
            lines.append('  Path: {}'.format(path))
    logging.info('\n'.join(lines))

def reconcile_old_instances(from_dative, from_old):
    """Takes a two lists of dicts, the first representing the OLD instances
    that Dative knows about and the second representing the OLD instances that
    the local OLD is serving. Reconcile them by returning a new list of dicts
    where Dative's name and id values override the values from the OLD, in the
    cases where there is a match based on URL.
    """
    ret = []
    for oi in from_old:
        our_oi = oi.copy()
        key = our_oi['url']
        matches = [doi for doi in from_dative if doi['url'] == key]
        if matches:
            our_oi['name'] = matches[0]['name']
            our_oi['id'] = matches[0]['id']
        ret.append(our_oi)
    return ret


def slugify(thing):
    return ''.join(
        c for c in thing.lower() if c in 'abcdefghijklmnopqrstuvwxyz1234567890')


def validate_new_old_instance(new_old_name, new_old_short_name,
                              known_old_instances):
    dbname = slugify(new_old_short_name)
    new_old_name = new_old_name.strip()
    if not new_old_name:
        new_old_name = new_old_short_name.strip()
    if not dbname:
        return (None, f'The short name "{new_old_short_name}" must contain'
                        f' at least one letter or number. All other'
                        f' characters are removed.')
    if dbname.startswith(tuple('1234567890')):
        return (None, f'The short name "{new_old_short_name}" contains a'
                        f' number as its first character (after sanitization).'
                        f' This is prohibited. Please choose another short'
                        f' name.')
    if dbname in [oi.get('name') for oi in known_old_instances]:
        return (None, f'There is already a locally served OLD instance with'
                        f' a short name that matches "{new_old_short_name}"'
                        f' (after sanitization: "{dbname}"). Please shoose'
                        f' another short name.')
    return (new_old_name, dbname), None


class DativeTop(toga.App):
    """The DativeTop Toga app

    This is a very minimal native ape with standard menus in the menubar and
    a ``toga.WebView`` that displays the locally served Dative CoffeeScript SPA.
    """

    def __init__(self, stop_serving_dative, stop_serving_old, *args, **kwargs):
        self.dativetop_settings = get_settings(config_path=CONFIG_PATH)
        self._about_window = None
        self.dative_gui = None
        self.dative_app_settings = None
        self.reconciled_old_instances = []
        self.old_instance_widgets = {}
        self.new_old_name_input = toga.TextInput(style=Pack(flex=1),)
        self.new_old_short_name_input = toga.TextInput(
            style=Pack(flex=1), on_change=self.remove_create_new_old_error,)
        self.create_new_old_button = self.get_create_new_old_button()
        self.new_old_instance_form_validation_label = (
            self.get_new_old_instance_form_validation_label())
        self.new_old_instance_form = self.get_new_old_instance_form_gui()
        self.old_instances_table = self.get_old_instances_table()
        self.old_instances_box = self.get_old_instances_box()
        self.dativetop_gui = self.generate_dativetop_gui()
        # self.main_window = None
        self.commands = None
        self.stop_serving_dative = stop_serving_dative
        self.stop_serving_old = stop_serving_old
        super(DativeTop, self).__init__(*args, **kwargs)

    def startup(self):
        """On startup, build the Dative (WebView) and DativeTop (Toga native)
        GUIs and display the Dative one.
        """
        self.main_window = toga.MainWindow(
            title=self.name,
            size=(1500, 1000),
            position=(0, 0),
        )
        self.set_commands()
        self.dative_gui = self.get_dative_gui()
        self.main_window.content = self.dative_gui
        self.main_window.show()

    def get_dative_gui(self):
        dative_gui = toga.WebView(style=Pack(flex=1))
        dative_gui.url = DATIVE_URL
        return dative_gui

    def calculate(self, widget):
        print('CALCULATE!')

    def get_old_instances_list(self):
        return sorted([
            (oi['name'], oi['url'], get_size_of_old_instance(oi),) for
            oi in self.reconciled_old_instances])

    def get_old_instances_table(self):
        return toga.Table(
            style=Pack(padding_top=20),
            headings=OLD_INSTANCES_TABLE_HEADINGS,
            data=self.get_old_instances_list(),
            on_select=copy_old_instance_url,)

    def get_old_instance_box(self, oi_dict):
        oi_label_style = Pack(text_align=LEFT)
        return toga.Box(
            style=Pack(direction=COLUMN),
            children=[
                toga.Label(
                    '\u2022 OLD \u201c{}\u201d being served at URL'
                    ' \u201c{}\u201d.'.format(oi_dict['name'], oi_dict['url']),
                    style=oi_label_style,),
            ],
        )

    def get_old_instances_box(self):
        ret = toga.Box(
            style=Pack(direction=COLUMN),
            children=[
                toga.Label(
                    '',
                    style=Pack(text_align=LEFT),),],)
        for oi_url, oi_widget_dict in self.old_instance_widgets.items():
            ret.add(oi_widget_dict['widget'])
        return ret

    def refresh_old_instance_widgets(self):
        for oi in self.reconciled_old_instances:
            oi_url = oi['url']
            existing_oi_widget = self.old_instance_widgets.get(oi_url)
            if existing_oi_widget:
                continue
            widget = self.get_old_instance_box(oi)
            self.old_instance_widgets[oi_url] = {'widget': widget}

    def refresh_old_instances_box(self):
        for oi_url, oi_widget_dict in self.old_instance_widgets.items():
            oi_widget = oi_widget_dict['widget']
            if oi_widget not in self.old_instances_box.children:
                self.old_instances_box.add(oi_widget)
        self.old_instances_box.refresh_sublayouts()

    def refresh_old_instances_table(self):
        self.old_instances_table.data = self.get_old_instances_list()

    def get_new_old_instance_form_gui(self):
        """Return the Toga ``Box`` that holds the input fields and buttons for
        creating a new OLD instance.
        """
        return toga.Box(
            style=Pack(direction=COLUMN, padding_top=30),
            children=[
                toga.Box(
                    style=Pack(direction=ROW, padding=5),
                    children=[
                        toga.Label('Name', style=Pack(width=100, text_align=LEFT)),
                        self.new_old_name_input,],),
                toga.Box(
                    style=Pack(direction=ROW, padding=5),
                    children=[
                        toga.Label('Short Name', style=Pack(width=100, text_align=LEFT)),
                        self.new_old_short_name_input,],),
                toga.Box(
                    style=Pack(direction=ROW),
                    children=[
                        self.create_new_old_button,],),
                toga.Box(
                    style=Pack(direction=ROW,),
                    children=[
                        self.new_old_instance_form_validation_label,],),],)

    def get_create_new_old_button(self):
        return toga.Button(
            'Create New OLD',
            style=Pack(padding_top=5),
            on_press=self.create_new_old_instance,)

    def get_new_old_instance_form_validation_label(self):
        return toga.Label('', style=Pack(flex=1, color='Red',),)

    def generate_dativetop_gui(self):
        # Styles
        dt_component_style = Pack(
            direction=COLUMN,
            padding_top=30,
            padding_left=30,
            padding_right=30,)
        dt_component_label_style = Pack(text_align=LEFT, font_size=20)
        row_button_style = Pack(flex=0, padding_top=20, padding_right=10,)

        # Text
        dative_browser_button_text = 'Open Dative in Browser'
        dative_button_text = 'Dative'
        dative_copy_url_button_text = 'Copy Dative URL'
        dative_help_text = (
            f'Your local Dative app is being served at {DATIVE_URL}.\n'
            f'Click the "{dative_button_text}" button to use it.\n'
            f'Click the "{dative_browser_button_text}" to open it in a web browser.\n')
        dativetop_help_text = (
            f'DativeTop is an application for linguistic data management.\n'
            f'DativeTop lets you create, use and manage Online Linguistic'
                f' Database (OLD) instances on your local machine.\n'
            f'DativeTop lets you use the Dative graphical user interface to'
                f' work with your OLD instances.\n')
        old_help_text = (
            f'These are your local Online Linguistic Database instances.\n'
            f'Click a row to copy its URL to your clipboard.\n'
            f'You may have to manually tell Dative about these OLD instances by'
                f' adding new "server" instances for them under Dative >'
                f' Application Settings.\n')
        # Structure
        return toga.Box(
            style=Pack(direction=COLUMN, padding_top=5, padding_right=200, padding_left=200, padding_bottom=5),
            children=[

                toga.Box(
                    style=dt_component_style,
                    children=[
                        toga.Label('DativeTop', style=dt_component_label_style),
                        toga.Box(
                            style=Pack(
                                direction=COLUMN, padding=30),
                            children=[
                                toga.Label(dativetop_help_text,
                                           style=Pack(text_align=LEFT)),],),],),

                # Dative Box
                toga.Box(
                    style=dt_component_style,
                    children=[
                        toga.Label('Dative', style=dt_component_label_style),
                        toga.Box(
                            style=Pack(
                                direction=COLUMN, padding=30),
                            children=[
                                toga.Label(dative_help_text,
                                           style=Pack(text_align=LEFT)),
                                toga.Box(
                                    style=Pack(direction=ROW),
                                    children=[
                                        toga.Button(
                                            dative_button_text,
                                            on_press=self.view_dative_gui_cmd,
                                            style=row_button_style,),
                                        toga.Button(
                                            dative_browser_button_text,
                                            on_press=self.visit_dative_in_browser_cmd,
                                            style=row_button_style,),
                                        toga.Button(
                                            dative_copy_url_button_text,
                                            on_press=self.copy_dative_url_to_clipboard_cmd,
                                            style=row_button_style,),
                                        ],),],),],),

                # OLD Box
                toga.Box(
                    style=dt_component_style,
                    children=[
                        toga.Label(
                            'Online Linguistic Database Instances',
                            style=dt_component_label_style),
                        toga.Box(
                            style=Pack(
                                direction=COLUMN, padding=30),
                            children=[
                                toga.Label(
                                    old_help_text,
                                    style=Pack(text_align=LEFT)),
                                self.old_instances_box,
                                toga.Box(
                                    style=Pack(direction=ROW),
                                    children=[self.new_old_instance_form,],),],),],),],)

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
        pyperclip.copy(str(self.dative_gui.evaluate(COPY_SELECTION_JS)))

    def cut_cmd(self, sender):
        pyperclip.copy(str(self.dative_gui.evaluate(CUT_SELECTION_JS)))

    def select_all_cmd(self, sender):
        self.dative_gui.evaluate(SELECT_ALL_JS)

    def reset_dative_app_settings_cmd(self, sender):
        self.dative_gui.evaluate(DESTROY_DATIVE_APP_SETTINGS)
        self.reload_cmd(sender)

    def get_dative_app_settings(self):
        """Extract the application settings dictionary from the Dative App.
        """
        app_set_str = str(
            self.dative_gui.evaluate(GET_DATIVE_APP_SETTINGS)).strip()
        if app_set_str:
            try:
                return json.loads(app_set_str)
            except:
                return {}
        return {}

    def set_dative_app_settings(self, dative_app_settings_dict):
        """Set the application settings dictionary in the Dative App to a JSON
        string created by serializing ``dative_app_settings_dict``.
        """
        y = self.main_window.content
        self.main_window.content = self.dative_gui
        to_eval = SET_DATIVE_APP_SETTINGS.format(
            dative_app_settings=json.dumps(dative_app_settings_dict))
        print('EVAL THIS!:')
        print(to_eval)
        x = self.dative_gui.evaluate(to_eval)
        print('ret val:')
        print(x)
        # self.main_window.content = y

        print('\n\n\nDative app settings now')
        pprint.pprint(len(self.really_get_dative_app_settings()['servers']))

    def paste_cmd(self, sender):
        self.dative_gui.evaluate(paste_js(pyperclip.paste().replace('`', r'\`')))

    def reload_cmd(self, sender):
        """This should be the equivalent of a browser refresh of the Dative
        SPA.
        """
        self.dative_gui.url = DATIVE_URL

    def really_get_dative_app_settings(self):
        """Return the Dative application settings (from localStorage in the
        JavaScript process). If they are empty, try to retrieve them after
        display Dative in the WebView.
        """
        dative_app_settings = self.get_dative_app_settings()
        if not dative_app_settings:
            self.main_window.content = self.dative_gui
            dative_app_settings = self.get_dative_app_settings()
        return dative_app_settings

    @property
    def old_base_url(self):
        return (f'http://{self.dativetop_settings["dativetop_ip"]}:'
                f'{self.dativetop_settings["dativetop_old_port"]}/')

    def get_base_old_dict(self, old_name):
        return {'corpusServerURL': None,
                'id': generate_uuid(),
                'name': old_name,
                'serverCode': None,
                'type': 'OLD',
                'url': f'{self.old_base_url}{old_name}',
                'website': 'http://www.onlinelinguisticdatabase.org'}

    def introspect_old_instances(self):
        """Return a list of OLD instance dicts, deduced by inspecting the
        .sqlite files listed under ``config['old_db_dirpath']``. Aside from the
        defaults, the file system data gives us the name and local URL of each
        instance.
        """
        old_instances = []
        old_db_dirpath = self.dativetop_settings.get('old_db_dirpath')
        if old_db_dirpath and os.path.isdir(old_db_dirpath):
            for e_name in os.listdir(old_db_dirpath):
                e_path = os.path.join(old_db_dirpath, e_name)
                if os.path.isfile(e_path):
                    old_name, ext = os.path.splitext(e_name)
                    if ext == '.sqlite':
                        old_instance = self.get_base_old_dict(old_name)
                        old_instance['local_path'] = e_path
                        old_instances.append(old_instance)
        return old_instances

    def view_dativetop_gui_cmd(self, sender):
        self.set_reconciled_old_instances()
        self.refresh_old_instance_widgets()
        self.refresh_old_instances_box()
        self.dativetop_gui.refresh_sublayouts()
        self.main_window.content = self.dativetop_gui

    def set_reconciled_old_instances(self):
        """Determine the OLD instances known by Dative, the OLD and DativeTop. Set
        ``self.reconciled_old_instances`` to a list of dicts representing the
        OLD instances that DativeTop knows about.

        - The OLD instances that the local OLD web service knows about is
          determined by the list of SQLite files that are present in the
          oldinstances/dbs/ directory.
        - Dative keeps an in-memory account of the OLDs it knows about in its
          localStorage['dativeApplicationSettings'] JSON string.
        """
        self.dative_app_settings = self.really_get_dative_app_settings()
        old_instances_dative_knows = self.dative_app_settings.get('servers', [])
        log_old_instances('Dative knows about these OLD instances:',
                          old_instances_dative_knows)
        old_instances = self.introspect_old_instances()
        log_old_instances('The local OLD is serving these OLD instances:',
                          old_instances, include_paths=True)
        self.reconciled_old_instances = reconcile_old_instances(
            old_instances_dative_knows, old_instances)
        log_old_instances('DativeTop should know about these OLD instances:',
                          self.reconciled_old_instances)
        logging.info(pprint.pformat(self.reconciled_old_instances))

    def view_dative_gui_cmd(self, sender):
        self.main_window.content = self.dative_gui

    def copy_dative_url_to_clipboard_cmd(self, sender):
        pyperclip.copy(DATIVE_URL)

    def display_create_new_old_error(self, errstr):
        logging.warning(
            'User-supplied values for creating a new OLD instance were invalid.'
            ' Error: "%s".', errstr)
        self.new_old_instance_form_validation_label.text = errstr

    def remove_create_new_old_error(self, sender):
        self.new_old_instance_form_validation_label.text = ''

    def create_new_old_instance(self, sender):
        """Create a new OLD instance: an SQLite file and a directory.
        Shell out to the ``initialize_old`` executable to do this.
        """
        new_old_name = self.new_old_name_input.value
        new_old_short_name = self.new_old_short_name_input.value
        logging.info(
            'Attempting to create a new OLD instance named "%s" with short name'
            ' "%s".', new_old_name, new_old_short_name,)
        instance, err = validate_new_old_instance(
            new_old_name, new_old_short_name, self.reconciled_old_instances)
        if err:
            return self.display_create_new_old_error(err)
        name, short_name = instance
        logging.info(
            'The short name "%s" is valid name for a new OLD instance.', short_name)
        try:
            self.create_new_old_button.enabled = False
            cmd = shlex.split(
                f'initialize_old config.ini {short_name}')
            logging.info('Command to create new OLD: %s.', cmd)
            ret = subprocess.check_output(cmd)
            logging.info(
                'Output from running command to create new OLD: %s.', ret)
        except Exception as exc:
            logging.error(
                'Unexpected exception raised when attempting to create a new'
                ' OLD. Exception %s (%s).', exc, type(exc))
            self.display_create_new_old_error(
                f'Sorry, we were unable to create a new OLD instance with name'
                f' "{short_name}".')
        else:
            self.set_reconciled_old_instances()
            self.refresh_old_instance_widgets()
            self.refresh_old_instances_box()
            self.dativetop_gui.refresh_sublayouts()
            self.dativetop_gui.refresh()
        finally:
            self.create_new_old_button.enabled = True

    def back_cmd(self, sender):
        self.dative_gui.evaluate('window.history.back();')

    def forward_cmd(self, sender):
        self.dative_gui.evaluate('window.history.forward();')

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

        reset_cmd = toga.Command(
            self.reset_dative_app_settings_cmd,
            label='Reset Dative',
            shortcut='k',
            group=toga.Group.VIEW)

        view_dativetop_gui_cmd = toga.Command(
            self.view_dativetop_gui_cmd,
            label='DativeTop',
            shortcut='t',
            group=toga.Group.VIEW,
            order=2)

        view_dative_gui_cmd = toga.Command(
            self.view_dative_gui_cmd,
            label='Dative',
            shortcut='d',
            group=toga.Group.VIEW,
            order=3)

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


def real_main():
    stop_serving_dative = serve_dative()
    stop_serving_old = serve_old()
    launch_dativetop(stop_serving_dative, stop_serving_old)


def main():
    # demo_main()
    real_main()
