"""DativeTop: Serve OLD

Functionality for serving the OLD Pyramid web service locally, in a new
process, using the pserve Python server.
"""

from dativetop.constants import IP, OLD_PORT, OLD_URL, OLD_DIR
from dativetop.serve.pyramidapp import serve_pyr


def serve_old():
    """Serve the OLD locally in a separate thread that forks a subprocess that
    invokes the pserve executable. Return a function that stops serving the OLD.
    """
    return serve_pyr('The OLD', IP, OLD_PORT, OLD_URL, OLD_DIR)
