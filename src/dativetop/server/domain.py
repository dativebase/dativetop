"""Domain entities for DativeTop:

Defines the following named tuples and corresponding constructor functions:

- ``OLDInstance``, constructor: ``construct_old_instance``
- ``DativeApp``, constructor: ``construct_dative_app``
- ``OLDService``, constructor: ``construct_old_service``

"""

from collections import namedtuple
import string
import pprint


OLDInstance = namedtuple(
    'OLDInstance', (
        'slug',  # (str, unique among OLD instances at a given OLDService.url,
                 # e.g., "oka")
        'name',  # (str, human readable name, e.g., "Okanagan")
        'url',  # (str, URL, typically the slug suffixed to the URL of a local
                # OLD web service)
        'leader',  # (str, URL, the URL of an external OLD instance that this
                   # OLD instance follows and syncs with)
        'state',  # (str, forced choice, one of "synced", "syncing", or "not
                  # in sync")
        'is_auto_syncing'  # (bool, setting indicates whether DativeTop should
                           # continuously and automatically keep this local
                           # OLDInstance in sync with its leader.)
    ))


LICIT_SLUG_CHARACTERS = string.ascii_lowercase + string.digits


def slug_validator(potential_slug):
    if not potential_slug:
        return None, f'A slug cannot be an empty string'
    sanitized_slug = ''.join(c for c in potential_slug if c in LICIT_SLUG_CHARACTERS)
    if potential_slug == sanitized_slug:
        return potential_slug, None
    return (
        None,
        f'Slugs can only contain characters from this string:'
        f' "{LICIT_SLUG_CHARACTERS}".')


SYNCED_STATE = 'synced'
SYNCING_STATE = 'syncing'
NOT_SYNCED_STATE = 'not synced'
OLD_INSTANCE_STATES = (
    SYNCED_STATE,
    SYNCING_STATE,
    NOT_SYNCED_STATE,
)


def state_validator(potential_state):
    if potential_state in OLD_INSTANCE_STATES:
        return potential_state, None
    delim = '", "'
    return None, f'State must be one of "{delim.join(OLD_INSTANCE_STATES)}".'


AttributeSchema = namedtuple('AttributeSchema', ('type', 'default', 'validator'))


old_instance_schema = {
    'slug': AttributeSchema(
        type=str,
        default='',
        validator=slug_validator,),
    'name': AttributeSchema(
        type=str,
        default='',
        validator=None,),
    'url': AttributeSchema(
        type=str,
        default='',
        validator=None,),
    'leader': AttributeSchema(
        type=str,
        default='',
        validator=None,),
    'state': AttributeSchema(
        type=str,
        default=NOT_SYNCED_STATE,
        validator=state_validator,),
    'is_auto_syncing': AttributeSchema(
        type=bool,
        default=False,
        validator=None,),
}


DativeApp = namedtuple(
    'DativeApp', (
        'url',  # (str, URL, the local URL where the DativeApp is being served)
    ))


dative_app_schema = {
    'url': AttributeSchema(
        type=str,
        default='',
        validator=None,),
}


OLDService = namedtuple(
    'OLDService', (
        'url',  # (str, URL, the local URL where the OLD service is being
                # served)
    ))


old_service_schema = {
    'url': AttributeSchema(
        type=str,
        default='',
        validator=None,),
}


def construct(namedtuple_, schema, **kwargs):
    new_kwargs = {k: kwargs.get(k, schema[k].default) for
                  k in namedtuple_._fields}
    wrong_types = [
        (f'Value "{v}" of type "{type(v)}" is not of expected type'
         f' "{schema[k].type}" for attribute "{k}".') for
        k, v in new_kwargs.items() if
        not isinstance(v, schema[k].type)]
    if wrong_types:
        return None, ' '.join(sorted(wrong_types))
    validators = {
        k: schema[k].validator for
        k, v in new_kwargs.items() if schema[k].validator}
    validations = [
        validator(new_kwargs[k]) for k, validator in validators.items()]
    validation_failures = [err for _, err in validations if err]
    if validation_failures:
        return None, ' '.join(sorted(validation_failures))
    return namedtuple_(**new_kwargs), None


def construct_old_instance(**kwargs):
    """Construct an OLDInstance tuple given keyword arguments.

    Uses defaults from ``old_instance_schema`` when no value is supplied.
    Performs type-based and validator-based validation prior to construction of
    the tuple. Always returns a "maybe OLDInstance" 2-tuple, where the second
    element is an error string or None.
    """
    return construct(OLDInstance, old_instance_schema, **kwargs)


def construct_dative_app(**kwargs):
    return construct(DativeApp, dative_app_schema, **kwargs)


def construct_old_service(**kwargs):
    return construct(OLDService, old_service_schema, **kwargs)


if __name__ == '__main__':

    test_old_instance, err = construct_old_instance(
        slug='oka',
        name='Okanagan OLD',
        url='http://127.0.0.1:5679/oka',
        leader='',
        state=NOT_SYNCED_STATE,
        is_auto_syncing=False)
    assert not err
    pprint.pprint(test_old_instance)

    test_old_instance, err = construct_old_instance(
        slug='oka!',
        name='Okanagan OLD',
        url='http://127.0.0.1:5679/oka',
        leader='',
        state='some garbage',
        is_auto_syncing=False)
    assert err == (
        'Slugs can only contain characters from this string: '
        '"abcdefghijklmnopqrstuvwxyz0123456789". State must be one of "synced",'
        ' "syncing", "not synced".')
    print(err)

    test_old_instance, err = construct_old_instance(
        slug='oka',
        name=2,
        url='http://127.0.0.1:5679/oka',
        leader='',
        state='some garbage',
        is_auto_syncing=None)
    assert err == (
        'Value "2" of type "<class \'int\'>" is not of expected type "<class'
        ' \'str\'>" for attribute "name". Value "None" of type "<class \'NoneType\'>"'
        ' is not of expected type "<class \'bool\'>" for attribute'
        ' "is_auto_syncing".')
    print(err)

    test_dative_app, err = construct_dative_app(
        url='http://127.0.0.1:5678/',)
    assert not err
    print(test_dative_app)

    test_old_service, err = construct_old_service(
        url=3.14159,)
    assert err == (
        'Value "3.14159" of type "<class \'float\'>" is not of expected type'
        ' "<class \'str\'>" for attribute "url".')
    print(err)
