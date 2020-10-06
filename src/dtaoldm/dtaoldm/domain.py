"""Domain entities for DativeTop:

Defines the following domain entities:

- OLD instance: an Online Linguistic Database instance.
- Dative app: a Dative application, presumably running locally.
- OLD service: an Online Linguistic Database service that might be serving OLD
  instances.

These domain entites are encoded as named tuples. Each has a constructor, which
implements validation. See the ``CONSTRUCTORS`` dict which maps the canonical
type names of the domain entities to their constructor functions, which return
instances of the appropriate namedtuple on success.

Named tuples antd their corresponding constructor functions:

- namedtuple: ``OLDInstance``, constructor: ``construct_old_instance``
- namedtuple: ``DativeApp``, constructor: ``construct_dative_app``
- namedtuple: ``OLDService``, constructor: ``construct_old_service``

"""

from collections import namedtuple
import string

import dtaoldm.utils as u


OLD_INSTANCE_TYPE = 'old-instance'
DATIVE_APP_TYPE = 'dative-app'
OLD_SERVICE_TYPE = 'old-service'

LICIT_SLUG_CHARACTERS = string.ascii_lowercase + string.digits
SYNCED_STATE = 'synced'
SYNCING_STATE = 'syncing'
NOT_SYNCED_STATE = 'not synced'
OLD_INSTANCE_STATES = (
    SYNCED_STATE,
    SYNCING_STATE,
    NOT_SYNCED_STATE,
)


AttributeSchema = namedtuple('AttributeSchema', ('type', 'default', 'validator'))

ID_SCHEMA = AttributeSchema(
    type=str,
    default=u.get_uuid,
    validator=None,)


def construct(namedtuple_, schema, **kwargs):
    """
    Construct a new namedtuple using ``namedtuple_`` and the attribute/value
    pairs in ``kwargs``. Use ``schema`` to validate the arguments. Return a
    "maybe namedtuple_", i.e., a 2-tuple where the second element is None in
    the happy path, but an error string in the failure case.
    """
    new_kwargs = {}
    for k in namedtuple_._fields:
        v = kwargs.get(k, schema[k].default)
        if callable(v):
            v = v()
        new_kwargs[k] = v
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


# ==============================================================================
# Validators
# ==============================================================================

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


def state_validator(potential_state):
    if potential_state in OLD_INSTANCE_STATES:
        return potential_state, None
    delim = '", "'
    return None, f'State must be one of "{delim.join(OLD_INSTANCE_STATES)}".'


# ==============================================================================
# OLD Instance (domain entity)
# ==============================================================================

OLDInstance = namedtuple(
    'OLDInstance', (
        'id',  # (str, UUID)
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

old_instance_schema = {
    'id': ID_SCHEMA,
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

def construct_old_instance(**kwargs):
    """Construct an OLDInstance tuple given keyword arguments.

    Uses defaults from ``old_instance_schema`` when no value is supplied.
    Performs type-based and validator-based validation prior to construction of
    the tuple. Always returns a "maybe OLDInstance" 2-tuple, where the second
    element is an error string or None.
    """
    return construct(OLDInstance, old_instance_schema, **kwargs)


# ==============================================================================
# Dative App (domain entity)
# ==============================================================================

DativeApp = namedtuple(
    'DativeApp', (
        'id',  # (str, UUID)
        'url',  # (str, URL, the local URL where the DativeApp is being served)
    ))


dative_app_schema = {
    'id': ID_SCHEMA,
    'url': AttributeSchema(
        type=str,
        default='',
        validator=None,),
}

def construct_dative_app(**kwargs):
    return construct(DativeApp, dative_app_schema, **kwargs)


# ==============================================================================
# OLD Service (domain entity)
# ==============================================================================

OLDService = namedtuple(
    'OLDService', (
        'id',  # (str, UUID)
        'url',  # (str, URL, the local URL where the OLD service is being
                # served)
    ))


old_service_schema = {
    'id': ID_SCHEMA,
    'url': AttributeSchema(
        type=str,
        default='',
        validator=None,),
}

def construct_old_service(**kwargs):
    return construct(OLDService, old_service_schema, **kwargs)


# ==============================================================================
# Constructors
# ==============================================================================

CONSTRUCTORS = {
    DATIVE_APP_TYPE: construct_dative_app,
    OLD_INSTANCE_TYPE: construct_old_instance,
    OLD_SERVICE_TYPE: construct_old_service,
}
