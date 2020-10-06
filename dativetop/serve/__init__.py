"""DativeTop Serve package contains modules for serving the various DativeTop
sub-services:

- Dative GUI
- OLD Web Service
- DativeTop GUI
- DativeTop Web Service

"""

from dativetop.serve.dative import serve_dative
from dativetop.serve.old import serve_old
from dativetop.serve.dativetopgui import serve_dativetop_gui
from dativetop.serve.dativetopserver import serve_dativetop_server


__all__ = (
    'serve_dative',
    'serve_dativetop_gui'
    'serve_dativetop_server'
    'serve_old',
)
