"""DativeTop: Serve DativeTop Server, a Pyramid web service

Functionality for serving the DativeTop Server Pyramid web service locally, in
a new process.
"""

from dativetop.constants import (
    IP,
    DATIVETOP_SERVER_DIR,
    DATIVETOP_SERVER_PORT,
    DATIVETOP_SERVER_URL,
)
from dativetop.serve.pyramidapp import serve_pyr



def serve_dativetop_server():
    """Serve the DativeTop Server locally in a separate thread that forks a
    subprocess that invokes the pserve executable. Return a function that stops
    serving the OLD.
    """
    return serve_pyr(
        'DativeTop Server', IP, DATIVETOP_SERVER_PORT, DATIVETOP_SERVER_URL,
        DATIVETOP_SERVER_DIR)
