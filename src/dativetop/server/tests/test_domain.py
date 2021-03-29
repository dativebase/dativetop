"""Domain Tests
"""

import pytest

import dativetopserver.domain as domain
import tests.utils as utils


@pytest.mark.parametrize(
    'kwargs, error', (
        utils.ConstructOLDInstanceCase(
            kwargs={
                'slug': 'oka',
                'name': 'Okanagan OLD',
                'url': 'http://127.0.0.1:5679/oka',
                'leader': '',
                'state': domain.NOT_SYNCED_STATE,
                'is_auto_syncing': False,},
            error=None
        ),

        utils.ConstructOLDInstanceCase(
            kwargs={
                'slug': 'oka!',
                'name': 'Okanagan OLD',
                'url': 'http://127.0.0.1:5679/oka',
                'leader': '',
                'state': 'some garbage',
                'is_auto_syncing': False,},
            error=(
                'Slugs can only contain characters from this string: '
                '"abcdefghijklmnopqrstuvwxyz0123456789". State must be one of'
                ' "synced", "syncing", "not synced".'),
        ),

        utils.ConstructOLDInstanceCase(
            kwargs={
                'slug': 'oka',
                'name': 2,
                'url': 'http://127.0.0.1:5679/oka',
                'leader': '',
                'state': 'some garbage',
                'is_auto_syncing': None,},
            error=(
                'Value "2" of type "<class \'int\'>" is not of expected type'
                ' "<class \'str\'>" for attribute "name". Value "None" of type'
                ' "<class \'NoneType\'>" is not of expected type "<class'
                ' \'bool\'>" for attribute "is_auto_syncing".'),
        ),

        utils.ConstructOLDInstanceCase(
            kwargs={'slug': 'oka',
                    'url': 'http://127.0.0.1:5678/',},
            error=None,
        ),

        utils.ConstructOLDInstanceCase(
            kwargs={'url': 3.14159,},
            error=(
                'Value "3.14159" of type "<class \'float\'>" is not of expected'
                ' type "<class \'str\'>" for attribute "url".'),
        ),
    )
)
def test_old_instance_construction(kwargs, error):
    _, err = domain.construct_old_instance(**kwargs)
    assert err == error
