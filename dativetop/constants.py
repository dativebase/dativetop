"""DativeTop Constants"""

import os


HERE = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(HERE, 'dativetop', 'config.json')

APP_NAME = 'DativeTop'
APP_ID = 'org.dativebase.dativetop'
ICONS_FILE_NAME = 'OLDIcon.icns'
ICONS_FILE_PATH = os.path.join('icons', ICONS_FILE_NAME)
IP = '127.0.0.1'

DATIVE_PORT = 5678
DATIVE_ROOT = os.path.join(HERE, 'src', 'dative', 'dist')
DATIVE_URL = 'http://{}:{}/'.format(IP, DATIVE_PORT)
DATIVE_WEB_SITE_URL = 'http://www.dative.ca/'
DATIVE_WEBSITE_URL = 'http://www.dative.ca/'


OLD_DIR = os.path.join(HERE, 'src', 'old')
OLD_LOGO_PNG_PATH = 'private_resources/icons-originals/OLD-logo.png'
OLD_PORT = 5679
OLD_URL = 'http://{}:{}/'.format(IP, OLD_PORT)
OLD_WEB_SITE_URL = 'http://www.onlinelinguisticdatabase.org/'
