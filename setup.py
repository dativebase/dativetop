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


logger = logging.getLogger(__file__)


def install_extras(self):
    """Override for Briefcase's ``install_extras`` method. It:

    - copies the OLD config file to the correct place,
    - copies the compiled Dative dist/ directory to the correct place, and
    - installs the OLD and its dependencies
    """
    src_pth = os.path.join(self.app_dir, 'src')
    old_pth = os.path.join(src_pth, 'old')
    dative_pth = os.path.join(src_pth, 'dative')
    old_store_pth = os.path.join(old_pth, 'store')
    for pth in (src_pth, old_pth, dative_pth, old_store_pth):
        if not os.path.exists(pth):
            os.makedirs(pth)
    logger.info('Created source directories under {}.'.format(src_pth))

    dative_src_pth = os.path.join('src', 'dative', 'dist')
    dative_dst_pth = os.path.join(self.app_dir, 'src', 'dative', 'dist')
    if os.path.exists(dative_dst_pth):
        shutil.rmtree(dative_dst_pth)
    shutil.copytree(dative_src_pth, dative_dst_pth)
    logger.info('Copied Dative build to {}.'.format(dative_dst_pth))

    old_cfg_src_pth = os.path.join('src', 'old', 'config.ini')
    old_cfg_dst_pth = os.path.join(self.app_dir, 'src', 'old', 'config.ini')
    shutil.copyfile(old_cfg_src_pth, old_cfg_dst_pth)
    logger.info('Copied OLD config file to {}.'.format(old_cfg_dst_pth))

    old_instance_src_dir = os.path.join(
        os.environ['OLD_PERMANENT_STORE'],
        os.environ['DFLT_DATIVETOP_OLD_NAME'])
    old_instance_dst_dir = os.path.join(
        old_store_pth,
        os.environ['DFLT_DATIVETOP_OLD_NAME'])
    shutil.copytree(old_instance_src_dir, old_instance_dst_dir)
    logger.info('Copied OLD directory structure from {} to {}.'.format(
        old_instance_src_dir, old_instance_dst_dir))

    old_db_file_name = '{}.sqlite'.format(os.environ['DFLT_DATIVETOP_OLD_NAME'])
    old_db_src = os.path.join(
        os.environ['OLD_DB_DIRPATH'],  # = oldinstances/dbs/
        old_db_file_name)
    old_db_dst = os.path.join(
        old_pth,  # = src/old/
        old_db_file_name)
    shutil.copyfile(old_db_src, old_db_dst)
    logger.info('Copied OLD database file from {} to {}.'.format(
        old_db_src, old_db_dst))

    # Set the environment variable so the OLD behaves correctly once its
    # thread is started.
    os.environ['OLD_PERMANENT_STORE'] = old_store_pth
    logger.info('Set OLD_PERMANENT_STORE to {}.'.format(
        os.environ['OLD_PERMANENT_STORE']))

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
    packages=find_packages(
        exclude=[
            'docs', 'tests',
            'windows', 'macOS', 'linux',
            'iOS', 'android',
            'django'
        ]
    ),
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: Apache Software License',
    ],
    package_data={
        'dativetop': ['src/dative'],
    },
    include_package_data=True,
    options={
        'app': {
            'formal_name': 'DativeTop',
            'bundle': 'org.dativebase',
            'icon': 'dativetop/icons/OLDIcon'
        },

        # Desktop/laptop deployments
        'macos': {
            'app_requires': [
                'toga-cocoa==0.3.0.dev9',
            ]
        },
        'linux': {
            'app_requires': [
                'toga-gtk==0.3.0.dev9',
            ]
        },
        'windows': {
            'app_requires': [
                'toga-winforms==0.3.0.dev9',
            ]
        },

        # Mobile deployments
        'ios': {
            'app_requires': [
                'toga-ios==0.3.0.dev9',
            ]
        },
        'android': {
            'app_requires': [
                'toga-android==0.3.0.dev9',
            ]
        },

        # Web deployments
        'django': {
            'app_requires': [
                'toga-django==0.3.0.dev9',
            ]
        },
    }
)
