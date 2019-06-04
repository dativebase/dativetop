#!/usr/bin/env python
import io
import logging
import os
import re
from setuptools import setup, find_packages
import shlex
import shutil
import subprocess
import sys

from briefcase.app import app


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__file__)


def install_extras(self):
    """Override for Briefcase's ``install_extras`` method. It:

    - creates needed directories under the platform-specific app directory
      (e.g., macOS/DativeTop.app/Contents/Resources/app/ for Mac OS builds),
    - copies the compiled Dative dist/ directory to app/src/dative/,
    - copies the OLD config file config.ini to app/src/old/,
    - copies the default OLD instance's directory structure to
      app/src/old/store/,
    - copies the default OLD instance's SQLite database file to app/src/old/,
      and
    - shells out to ``pip`` to install the OLD and its dependencies (in
      development mode) in the build directory's local Python.
    """
    src_pth = os.path.join(self.app_dir, 'src')
    old_pth = os.path.join(src_pth, 'old')
    dative_pth = os.path.join(src_pth, 'dative')
    old_store_pth = os.path.join(old_pth, 'store')
    for pth in (src_pth, old_pth, dative_pth, old_store_pth):
        if not os.path.exists(pth):
            os.makedirs(pth)
    logger.info('Created source directories under %s.', src_pth)

    private_resources_src_pth = os.path.join('dativetop', 'private_resources')
    private_resources_dst_pth = os.path.join(
        self.app_dir, 'dativetop', 'private_resources')
    if os.path.exists(private_resources_dst_pth):
        shutil.rmtree(private_resources_dst_pth)
    shutil.copytree(private_resources_src_pth, private_resources_dst_pth)
    logger.info('Copied DativeTop private resources to %s.', private_resources_dst_pth)

    dative_src_pth = os.path.join('src', 'dative', 'dist')
    dative_dst_pth = os.path.join(self.app_dir, 'src', 'dative', 'dist')
    if os.path.exists(dative_dst_pth):
        shutil.rmtree(dative_dst_pth)
    shutil.copytree(dative_src_pth, dative_dst_pth)
    logger.info('Copied Dative build to %s.', dative_dst_pth)

    old_cfg_src_pth = os.path.join('src', 'old', 'config.ini')
    old_cfg_dst_pth = os.path.join(self.app_dir, 'src', 'old', 'config.ini')
    shutil.copyfile(old_cfg_src_pth, old_cfg_dst_pth)
    logger.info('Copied OLD config file to %s.', old_cfg_dst_pth)

    old_instance_src_dir = os.path.join(
        os.environ['OLD_PERMANENT_STORE'],
        os.environ['DFLT_DATIVETOP_OLD_NAME'])
    old_instance_dst_dir = os.path.join(
        old_store_pth,
        os.environ['DFLT_DATIVETOP_OLD_NAME'])
    if os.path.exists(old_instance_dst_dir):
        shutil.rmtree(old_instance_dst_dir)
    shutil.copytree(old_instance_src_dir, old_instance_dst_dir)
    logger.info('Copied OLD directory structure from %s to %s.',
                old_instance_src_dir, old_instance_dst_dir)

    old_db_file_name = '{}.sqlite'.format(os.environ['DFLT_DATIVETOP_OLD_NAME'])
    old_db_src = os.path.join(
        os.environ['OLD_DB_DIRPATH'],  # = oldinstances/dbs/
        old_db_file_name)
    old_db_dst = os.path.join(
        old_pth,  # = src/old/
        old_db_file_name)
    if os.path.exists(old_db_dst):
        os.remove(old_db_dst)
    shutil.copyfile(old_db_src, old_db_dst)
    logger.info('Copied OLD database file from %s to %s.', old_db_src,
                old_db_dst)

    # Set the environment variable so the OLD behaves correctly once its
    # thread is started.
    os.environ['OLD_PERMANENT_STORE'] = old_store_pth
    logger.info('Set OLD_PERMANENT_STORE to %s.',
                os.environ['OLD_PERMANENT_STORE'])

    cmd = shlex.split(
        'pip install'
        ' --upgrade'
        ' --force-reinstall'
        ' --target={}'
        ' src/old/[testing]'.format(self.app_dir))
    subprocess.check_output(
        cmd,
        stderr=subprocess.STDOUT)
    logger.info('Installed the OLD.')


app.install_extras = install_extras


with io.open('./dativetop/__init__.py', encoding='utf8') as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


with io.open('README.rst', encoding='utf8') as readme:
    long_description = readme.read()


setup(
    name='dativetop',
    version=version,
    description='A linguistic data management application',
    long_description=long_description,
    author='Joel Dunham',
    author_email='jrwdunham@gmail.com',
    license='Apache Software License',
    install_requires=[
        'pyperclip',
    ],
    packages=find_packages(
        exclude=[
            'docs', 'tests',
            'windows', 'macOS', 'linux',
            'iOS', 'android',
            'django'
        ]
    ),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: Apache Software License',
    ],
    options={
        'app': {
            'formal_name': 'DativeTop',
            'bundle': 'org.dativebase',
        },

        # Desktop/laptop deployments
        'macos': {
            'icon': 'dativetop/icons/OLDIcon',
            'app_requires': [
                'toga-cocoa==0.3.0.dev11',
            ]
        },
        'linux': {
            'app_requires': [
                'toga-gtk==0.3.0.dev11',
            ]
        },
        'windows': {
            'app_requires': [
                'toga-winforms==0.3.0.dev11',
            ]
        },

        # Mobile deployments
        'ios': {
            'app_requires': [
                'toga-ios==0.3.0.dev11',
            ]
        },
        'android': {
            'app_requires': [
                'toga-android==0.3.0.dev11',
            ]
        },

        # Web deployments
        'django': {
            'app_requires': [
                'toga-django==0.3.0.dev11',
            ]
        },
    }
)
