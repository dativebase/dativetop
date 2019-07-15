"""Client code to the DativeTop Service.

"""

from collections import namedtuple
import codecs
import json
import locale
import sys
from time import sleep
import unicodedata

import requests



DativeTopService = namedtuple(
    'DativeTopService',
    (
        'url',
    )
)


def get(dts, since=None):
    return requests.get(dts.url).json()


def append(dts, appendables):
    return (f'you want to append these appendables to the DativeTop Server AOL:'
            f' {appendables}.')
