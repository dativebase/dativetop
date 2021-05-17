"""DativeTop: Serve DativeTop Server, a Pyramid web service

Functionality for serving the DativeTop Server Pyramid web service locally, in
a new process.
"""

import dativetop.utils as dtutils
from dativetop.constants import DATIVETOP_SERVER_DIR, DATIVETOP_SERVER_URL
from dativetop.serve.pyramidapp import serve_pyr



def serve_dativetop_server():
    """Serve the DativeTop Server locally in a separate thread that forks a
    subprocess that invokes the pserve executable. Return a function that stops
    serving the OLD.
    """
    # TODO: dynamically generate available DTServer URL ...
    return dtutils.Service(
        name='DTServer',
        url=DATIVETOP_SERVER_URL,
        stopper=serve_pyr(
            'DativeTop Server', DATIVETOP_SERVER_URL, DATIVETOP_SERVER_DIR))
