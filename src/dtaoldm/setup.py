import codecs
import os
import re
from setuptools import find_packages, setup


HERE = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(HERE, 'README.rst')) as readme:
    README = readme.read()



def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='dativetop-append-only-log-domain-model',
    version=find_version("dtaoldm", "__init__.py"),
    packages=find_packages(),
    include_package_data=True,
    description=('Domain entities and append-only log utilities for DativeTop, a'
                 ' linguistic data management application.'),
    long_description=README,
    author='Joel Dunham',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=['wheel'],
    extras_require={
        'dev': [
            'pytest',
        ]
    },
    entry_points={
        'console_scripts': [
            # 'some-name = some.dot.path:som_func',
        ],
    },
)
