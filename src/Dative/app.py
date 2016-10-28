#!/usr/bin/env python
"""This project has the following goal:

    Use toga to create a native Mac OS application that runs Dative and the
    OLD. It does the following:
    1. Downloads the OLD and its dependencies.
    2. Allows the user to configure multiple OLDs and serve them locally using
       a Python server.
    3. Downloads Dative and its dependencies and serves it.
    4. Creates a WebView instance in which to display Dative.
    5. Uses the toga interface machinery to create a native Senex, i.e., an
       administration system for creating and configuring OLDs and the Dative
       interface.
    6. Bundles it up using pybee Briefcase ...

TODOs:

    1. Changes to main menu:
       - list "Dative" instead of "python" in main menu
       - list 

"""

import toga
from colosseum import CSS
from rubicon.objc import get_selector, objc_method


DATIVE_WEBSITE_URL = 'http://www.dative.ca/'
DATIVE_URL = 'http://localhost:9000/'


class DativeWebView(toga.App):

    def startup(self):
        #TODO: how to get the screen in a cross-platform way?
        self.screen = toga.platform.NSScreen.mainScreen().visibleFrame
        width = self.screen.size.width * 0.8
        self.main_window = toga.MainWindow(
            self.name, size=(width, self.screen.size.height))
        self.main_window.app = self
        self.webview = toga.WebView(style=CSS(flex=1))
        self.main_window.content = self.webview
        self.webview.url = DATIVE_URL
        self.main_window.show()

    def create_menu(self):
        """Create the main menu.
        WARNING: only works for Mac OS X currently because toga has no
        cross-platform menu widgets yet.
        """

        print(toga.platform.NSBundle)

        """
        - menu (NSMenu: title, ...)
          - methods:
            - init
            - add(MenuItem, MenuItemSeparator)
            - (setSubmenu_forItem_ (could be `add` method on MenuItem...))
          - attrs:
            - title (label)

        - menu item (NSMenuItem)
          - methods:
            - init
            - add(Menu)
          - attrs:
            - title (label)
            - on_press (action)
            - key_equivalent

        - menu item separator (MSMenuItem.separatorItem())

        """

        # App menu
        app_name = self.name
        self.menu = toga.platform.NSMenu.alloc().initWithTitle_('MainMenu')

        self.app_menuItem = self.menu\
            .addItemWithTitle_action_keyEquivalent_(
                'Apple',
                None,
                '')
        submenu = toga.platform.NSMenu.alloc().initWithTitle_(app_name)
        menu_item = toga.platform.NSMenuItem.alloc()\
            .initWithTitle_action_keyEquivalent_(
                'About ' + app_name, None, '')
        submenu.addItem_(menu_item)
        submenu.addItem_(toga.platform.NSMenuItem.separatorItem())
        menu_item = toga.platform.NSMenuItem.alloc()\
            .initWithTitle_action_keyEquivalent_(
                'Quit ' + app_name,
                get_selector('terminate:'),
                "q")
        submenu.addItem_(menu_item)
        self.menu.setSubmenu_forItem_(submenu, self.app_menuItem)

        # Help menu
        self.help_menuItem = self.menu\
            .addItemWithTitle_action_keyEquivalent_(
                'Apple',  # This title attr seems to have no effect
                None,
                '')
        submenu = toga.platform.NSMenu.alloc().initWithTitle_('Fizz')
        #submenu = toga.platform.NSMenu.alloc().init()
        menu_item = MenuItem('Visit Dative web site', visit_dative_website)._impl
        submenu.addItem_(menu_item)
        self.menu.setSubmenu_forItem_(submenu, self.help_menuItem)

        # Set the menu for the app.
        self._impl.setMainMenu_(self.menu)


def visit_dative_website(menu_item):
    import webbrowser
    webbrowser.open(DATIVE_WEBSITE_URL)


class TogaMenuItem(toga.platform.NSMenuItem):

    @objc_method
    def onPress_(self, obj) -> None:
        print('onPress_ called')
        if self._interface.on_press:
            toga.platform.utils.process_callback(
                self._interface.on_press(self._interface))


class MenuItem:
    """Based on ``Button`` in toga_cocoa/widgets/button.
    """

    def __init__(self, label, on_press=None):
        self._config = {'label': label, 'on_press': on_press}
        self._create()

    def _create(self):
        self.create()
        self._configure(**self._config)

    def create(self):
        self._impl = TogaMenuItem.alloc().init()
        self._impl._interface = self
        self._impl.setTarget_(self._impl)
        self._impl.setAction_(get_selector('onPress:'))

    def _configure(self, label, on_press):
        self.label = label
        self.on_press = on_press

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        if value is None:
            self._label = ''
        else:
            self._label = str(value)
        self._set_label(value)

    def _set_label(self, label):
        self._impl.setTitle_(self.label)

    @property
    def on_press(self):
        return self._on_press

    @on_press.setter
    def on_press(self, handler):
        self._on_press = handler
        self._set_on_press(handler)

    def _set_on_press(self, value):
        pass


def inspect(t):
    for attr in dir(t):
        val = getattr(t, attr)
        print('{}: {}\n'.format(attr, val))


if __name__ == '__main__':
    icon = toga.Icon('./resources/OLDIcon.icns')
    app = DativeWebView('Dative', 'ca.dative.dative', icon=icon)
    app.main_loop()
