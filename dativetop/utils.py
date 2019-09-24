import io
import json
import logging
import os
import re

from dativetop.constants import (
    DATIVE_ROOT,
    HERE,
    OLD_DIR,
)


logger = logging.getLogger(__name__)


def get_dativetop_version():
    """Return the DativeTop version as a string by inspecting this package's
    __init__.py file.
    """
    version_file_path = os.path.join(HERE, 'dativetop', '__init__.py')
    try:
        with io.open(version_file_path, encoding='utf8') as version_file:
            version_match = re.search(
                r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
            if version_match:
                return version_match.group(1)
            logger.warning('Unable to find DativeTop version in {}'.format(
                version_file_path))
            return 'unknown'
    except Exception:
        logger.warning('Unable to find DativeTop version in {}'.format(version_file_path))
        return 'unknown'


def get_dative_version():
    """Return the Dative version as a string by parsing its package.json JSON
    NPM config file.
    """
    dative_pkg_path = os.path.join(DATIVE_ROOT, 'package.json')
    try:
        with io.open(dative_pkg_path) as filei:
            dative_pkj_json = json.load(filei)
        return dative_pkj_json['version']
    except Exception:
        logger.warning('Unable to find Dative package.json at {}'.format(dative_pkg_path))
        return 'unknown'


def get_old_version():
    """Return the OLD version by parsing its ource (setup.py or info.py) files.
    """
    old_info_path = os.path.join(HERE, 'old', 'views', 'info.py')
    old_setup_path = os.path.join(OLD_DIR, 'setup.py')
    if os.path.isfile(old_setup_path):
        try:
            with io.open(old_setup_path, encoding='utf8') as version_file:
                version_match = re.search(
                    r"^VERSION = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
                if version_match:
                    return version_match.group(1)
                raise RuntimeError("Unable to find OLD version string.")
        except Exception:
            logger.warning('Unable to find OLD setup.py at {}'.format(old_setup_path))
            return 'unknown'
    elif os.path.isfile(old_info_path):
        try:
            with io.open(old_info_path, encoding='utf8') as version_file:
                version_match = re.search(
                    r"^\s*['\"]version['\"]:\s+['\"]([^'\"]*)['\"]", version_file.read(), re.M)
                if version_match:
                    return version_match.group(1)
                raise RuntimeError("Unable to find OLD version string.")
        except Exception:
            logger.warning('Unable to find OLD info.py at {}'.format(old_info_path))
            return 'unknown'
    else:
        logger.warning('Neither of these files exist so unable to get OLD version: {}'
              ' {}'.format(old_setup_path, old_info_path))
        return 'unknown'


def bind(func, maybe):
  """Call ``func`` on the value (first element) of ``maybe`` iff its error
  (second element) is ``None``, otherwise return ``(None, error)``.
  """
  value, error = maybe
  if error is None:
      return func(val)
  return None, error
