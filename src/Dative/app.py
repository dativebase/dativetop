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
        """Create the main menu."""
        # Dative menu.
        dative_menu_item = toga.MenuItem(self.name)
        dative_menu = toga.Menu(self.name)
        about_menu_item = toga.MenuItem('About ' + self.name)
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


if __name__ == '__main__':
    icon = toga.Icon('src/Dative/icons/OLDIcon.icns')
    app = DativeWebView('Dative', 'ca.dative.dative', icon=icon)
    app.main_loop()
