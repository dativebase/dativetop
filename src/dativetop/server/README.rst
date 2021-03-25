================================================================================
  DativeTop Server
================================================================================

Pyramid application that exposes a single append-only log (AOL) endpoint at /
that can be read, with GET, and appended to, with PUT.

Serve it::

    $ pserve --reload config.ini http_port=4676 http_host=127.0.0.1
