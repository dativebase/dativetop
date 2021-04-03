================================================================================
  DativeTop Server
================================================================================

Pyramid application that exposes a single append-only log (AOL) endpoint at /
that can be read, with GET, and appended to, with PUT.

Serve it::

    $ pserve --reload config.ini http_port=4676 http_host=127.0.0.1

Run the tests::

    $ pytest

Install dependencies::

    $ pip install -e .

Build the database tables::

    $ initialize_dtserver_db config.ini

Open a shell::

    $ pshell config.ini


API
================================================================================

All database changes in this API are non-lossy, meaning that SQL ``update`` is
only used to deactivate a row, i.e., to set its ``end`` value to the current
date-time. All other updates are actually row deactivations followed by the
creation of a new row with the updated data.

- /old_service

  - GET: fetch the OLD service
  - PUT: update the URL of the OLD service

- /dative_app

  - GET: fetch the Dative app
  - PUT: update the URL of the Dative app

- /olds

  - GET: fetch all of the OLDs
  - POST: create a new OLD

- /olds/{old_id}

  - GET: fetch a specific OLD
  - PUT: update an OLD
  - DELETE: delete an OLD

- /olds/{old_id}/state

  - PUT: transition an OLD's state

- /sync_old_commands

  - POST: enqueue a new command
  - PUT: pop the next command off of the queue

- /sync_old_commands/{command_id}

  - GET: fetch a specific command
  - DELETE: complete a command
