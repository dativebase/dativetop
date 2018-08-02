#!/usr/bin/env python
import io
import re
from setuptools import setup, find_packages
import sys

with io.open('./dativetop/__init__.py', encoding='utf8') as version_file:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


with io.open('README.rst', encoding='utf8') as readme:
    long_description = readme.read()


def install_deps():
    """Reads requirements.txt and preprocess it
    to be feed into setuptools.

    This is the only possible way (we found)
    how requirements.txt can be reused in setup.py
    using dependencies from private github repositories.

    Links must be appendend by `-{StringWithAtLeastOneNumber}`
    or something like that, so e.g. `-9231` works as well as
    `1.1.0`. This is ignored by the setuptools, but has to be there.

    Warnings:
        to make pip respect the links, you have to use
        `--process-dependency-links` switch. So e.g.:
        `pip install --process-dependency-links {git-url}`

    Returns:
         list of packages and dependency links.
    """
    default = open('requirements/base.txt', 'r').readlines()
    new_pkgs = []
    links = []
    for resource in default:
        if 'git+ssh' in resource:
            pkg = resource.split('#')[-1]
            links.append(resource.strip() + '-9876543210')
            new_pkgs.append(pkg.replace('egg=', '').rstrip())
        else:
            new_pkgs.append(resource.strip())
    return new_pkgs, links

new_pkgs, links = install_deps()



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
            'bundle': 'org.dativebase'
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
