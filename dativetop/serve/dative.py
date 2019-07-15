"""DativeTop: Serve Dative

Functionality for serving the Dative CoffeeScript SPA locally, in a separate
thread, using a Python server.
"""

from dativetop.serve.servejsapp import serve_local_js_app
from dativetop.constants import (
    IP,
    DATIVE_PORT,
    DATIVE_URL,
    DATIVE_ROOT,
)


def serve_dative():
    return serve_local_js_app(
        'Dative', IP, DATIVE_PORT, DATIVE_URL, DATIVE_ROOT)
