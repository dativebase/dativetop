================================================================================
  DativeTop Append-Only Log Domain Model (dtaoldm)
================================================================================

The DativeTop Append-Only Log Domain Model (dtaoldm) defines the DativeTop
domain entities (OLDInstance, DativeApp, OLDService) and functions for
converting those entities to EAVT quadruples that can be stored in a
Python-native append-only log.


Install
================================================================================

Developed for Python >= 3.6.

Set up and activate a Python virtual environment::

    $ python -m venv venv
    $ source venv/bin/activate

Install in dev mode (where code changes are live)::

    $ pip install -e .[dev]

To run the tests::

    $ pytest tests/

To create a Wheel package::

    $ python setup.py sdist bdist_wheel


Usage
================================================================================

This example shows creating one of each of the following domain entities:
DativeApp, OLDService, OLDInstance::

    >>> import dtaoldm.domain as domain
    >>> old_service, _ = domain.construct_old_service(
    ...     url='http://127.0.0.1:5679/')
    >>> dative_app, _ = domain.construct_dative_app(
    ...     url='http://127.0.0.1:5678/')
    >>> old_instance, _ = domain.construct_old_instance(
    ...     slug='test', url='http://127.0.0.1:5679/test/')
    >>> old_service
    OLDService(url='http://127.0.0.1:5679/')
    >>> dative_app
    DativeApp(url='http://127.0.0.1:5678/')
    >>> old_instance
    OLDInstance(slug='test', name='', url='http://127.0.0.1:5679/test/',
    ...         leader='', state='not synced', is_auto_syncing=False)

Now we can convert these to "quads", EAVT (event, attribute, value, time)
4-tuples::

    >>> import dtaoldm.aol as aol
    >>> aol.instance_to_quads(dative_app, domain.DATIVE_APP_TYPE)
    (
        Quad(entity='5d6db659-3710-4226-bad7-518e43ed9e18',
             attribute='has',
             value='being',
             time='2019-07-15T17:43:57.212015'),
        Quad(entity='5d6db659-3710-4226-bad7-518e43ed9e18',
             attribute='is-a',
             value='dative-app',
             time='2019-07-15T17:43:57.212020'),
        Quad(entity='5d6db659-3710-4226-bad7-518e43ed9e18',
             attribute='has-url',
             value='http://127.0.0.1:5678/',
             time='2019-07-15T17:43:57.212025'),
    )

    >>> aol.instance_to_quads(old_service, domain.OLD_SERVICE_TYPE)
    (
        Quad(entity='2b214305-17e0-4617-ae64-b64b1528f1a7',
             attribute='has',
             value='being',
             time='2019-07-15T17:43:57.212300'),
        Quad(entity='2b214305-17e0-4617-ae64-b64b1528f1a7',
             attribute='is-a',
             value='old-service',
             time='2019-07-15T17:43:57.212308'),
        Quad(entity='2b214305-17e0-4617-ae64-b64b1528f1a7',
             attribute='has-url',
             value='http://127.0.0.1:5679/',
             time='2019-07-15T17:43:57.212315'),
    )

    >>> aol.instance_to_quads(old_instance, domain.OLD_INSTANCE_TYPE)
    (
        Quad(entity='9bc38782-99f8-4371-8b70-25c2e36c6802',
             attribute='has',
             value='being',
             time='2019-07-15T17:43:57.211720'),
        Quad(entity='9bc38782-99f8-4371-8b70-25c2e36c6802',
             attribute='is-a',
             value='old-instance',
             time='2019-07-15T17:43:57.211904'),
        Quad(entity='9bc38782-99f8-4371-8b70-25c2e36c6802',
             attribute='has-slug',
             value='test',
             time='2019-07-15T17:43:57.211914'),
        Quad(entity='9bc38782-99f8-4371-8b70-25c2e36c6802',
             attribute='has-name',
             value='',
             time='2019-07-15T17:43:57.211918'),
        Quad(entity='9bc38782-99f8-4371-8b70-25c2e36c6802',
             attribute='has-url',
             value='http://127.0.0.1:5679/test/',
             time='2019-07-15T17:43:57.211922'),
        Quad(entity='9bc38782-99f8-4371-8b70-25c2e36c6802',
             attribute='has-leader',
             value='',
             time='2019-07-15T17:43:57.211925'),
        Quad(entity='9bc38782-99f8-4371-8b70-25c2e36c6802',
             attribute='has-state',
             value='not synced',
             time='2019-07-15T17:43:57.211929'),
        Quad(entity='9bc38782-99f8-4371-8b70-25c2e36c6802',
             attribute='is-auto-syncing',
             value=False,
             time='2019-07-15T17:43:57.211932'),
    )
