"""DativeTop: Serve DativeTop GUI

Functionality for serving the Dative ClojureScript SPA locally, in a separate
thread, using a Python server.
"""

from dativetop.serve.servejsapp import serve_local_js_app
from dativetop.constants import (
    IP,
    DATIVETOP_GUI_PORT,
    DATIVETOP_GUI_URL,
    DATIVETOP_GUI_ROOT,
)


def serve_dativetop_gui():
    return serve_local_js_app(
        'DativeTop', IP, DATIVETOP_GUI_PORT, DATIVETOP_GUI_URL,
        DATIVETOP_GUI_ROOT)
