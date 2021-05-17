"""DativeTop Constants"""

import os


HERE = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(HERE, 'dativetop', 'config.json')

APP_FORMAL_NAME = 'DativeTop'
APP_NAME = 'dativetop'
APP_ID = 'org.dativebase.dativetop'
ICONS_FILE_NAME = 'dativetop.icns'
ICONS_FILE_PATH = os.path.join('resources', ICONS_FILE_NAME)
IP = '127.0.0.1'

DATIVE_ROOT = os.path.join(HERE, 'dative', 'dist')
DATIVE_WEB_SITE_URL = 'http://www.dative.ca/'

DATIVETOP_GUI_PORT = 5677
DATIVETOP_GUI_ROOT = os.path.join(HERE, 'dativetop', 'gui', 'target')
DATIVETOP_GUI_URL = f'http://{IP}:{DATIVETOP_GUI_PORT}/'

DATIVETOP_SERVER_PORT = 5676
DATIVETOP_SERVER_DIR = os.path.join(HERE, 'dativetop', 'server')
DATIVETOP_SERVER_URL = f'http://{IP}:{DATIVETOP_SERVER_PORT}/'

OLD_DIR = os.path.join(HERE, 'old')
OLD_LOGO_PNG_PATH = 'private_resources/icons-originals/OLD-logo.png'
OLD_WEB_SITE_URL = 'http://www.onlinelinguisticdatabase.org/'
