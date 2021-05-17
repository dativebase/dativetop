"""DativeTop: Serve Dative

Functionality for serving the Dative CoffeeScript SPA locally, in a separate
thread, using a Python server.
"""

from dativetop.serve.servejsapp import serve_local_js_app
from dativetop.constants import DATIVE_ROOT
import dativetop.utils as dtutils


def serve_dative(dative):
    return dtutils.Service(
        name=dative.name,
        url=dative.url,
        stopper=serve_local_js_app(dative.name, dative.url, DATIVE_ROOT))
