#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='Dative',
    version = '0.1',
    packages = find_packages(),
    options = {
        'app': {
            'formal_name': 'Dative',
            'dir': 'build/macOS',
            'bundle': 'ca.dative'
        },
        'macos': {
            'app_requires': [
                'toga-cocoa'
            ],
            'icon': 'src/Dative/icons/OLDIcon'
        }
    }
)
