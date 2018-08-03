#!/usr/bin/env python
import io
import os
import re
from setuptools import setup, find_packages
import shlex
import shutil
import subprocess
import sys

from briefcase.app import app


def install_extras(self):
    """Override for Briefcase's ``install_extras`` method. It:

    - copies the OLD config file to the correct place,
    - copies the compiled Dative dist/ directory to the correct place, and
    - installs the OLD and its dependencies
    """
    old_cfg_src_pth = os.path.join('src', 'old', 'config.ini')
    old_cfg_dst_pth = os.path.join(self.app_dir, 'src', 'old', 'config.ini')
    shutil.copyfile(old_cfg_src_pth, old_cfg_dst_pth)
    dative_src_pth = os.path.join('src', 'dative', 'dist')
    dative_dst_pth = os.path.join(self.app_dir, 'src', 'dative', 'dist')
    if os.path.exists(dative_dst_pth):
        shutil.rmtree(dative_dst_pth)
    shutil.copytree(dative_src_pth, dative_dst_pth)
    cmd = shlex.split(
        'pip install'
        ' --upgrade'
        ' --force-reinstall'
        ' --target={}'
        ' src/old/[testing]'.format(self.app_dir))
    print(subprocess.check_output(
        cmd,
        stderr=subprocess.STDOUT,
    ).decode('utf-8'))


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
