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

from dativetop.installextras import install_extras


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__file__)


app.install_extras = install_extras
app.dativetop_config_path = 'dativetop/config.json'


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
            'icon': 'src/dativetop/resources/dativetop',
            'app_requires': [
                'toga-cocoa==0.3.0.dev27',
            ]
        },
        'linux': {
            'app_requires': [
                'toga-gtk==0.3.0.dev27',
            ]
        },
        'windows': {
            'app_requires': [
                'toga-winforms==0.3.0.dev27',
            ]
        },

        # Mobile deployments
        'ios': {
            'app_requires': [
                'toga-ios==0.3.0.dev27',
            ]
        },
        'android': {
            'app_requires': [
                'toga-android==0.3.0.dev27',
            ]
        },

        # Web deployments
        'django': {
            'app_requires': [
                'toga-django==0.3.0.dev27',
            ]
        },
    }
)
