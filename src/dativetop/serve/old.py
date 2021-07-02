"""DativeTop: Serve OLD

Functionality for serving the OLD Pyramid web service locally, in a new
process, using the pserve Python server.
"""

from dativetop.constants import OLD_DIR
from dativetop.serve.pyramidapp import serve_pyr
import dativetop.utils as dtutils


def serve_old(old):
    """Serve the OLD locally in a separate thread that forks a subprocess that
    invokes the pserve executable. Return a function that stops serving the OLD.
    """
    return dtutils.Service(
        name=old.name,
        url=old.url,
        stopper=serve_pyr(old.name, old.url, OLD_DIR,
                          config='configlocal.ini'))
