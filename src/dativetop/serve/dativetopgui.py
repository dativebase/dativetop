"""DativeTop: Serve DativeTop GUI

Functionality for serving the Dative ClojureScript SPA locally, in a separate
thread, using a Python server.
"""

import os

from dativetop.constants import DATIVETOP_GUI_URL, DATIVETOP_GUI_ROOT
from dativetop.serve.servejsapp import serve_local_js_app
import dativetop.utils as dtutils


def _repair_dativetop_gui_index_html(old_service, dative_app, dtserver):
    index_path = os.path.join(DATIVETOP_GUI_ROOT, 'index.html')
    new_path = []
    with open(index_path) as f:
        for l in f:
            if 'window.DativeAppURL' in l:
                new_path.append('        window.DativeAppURL = "{}";\n'.format(dative_app.url))
            elif 'window.OLDServiceURL' in l:
                new_path.append('        window.OLDServiceURL = "{}";\n'.format(old_service.url))
            elif 'window.DativeTopServerURL' in l:
                new_path.append('        window.DativeTopServerURL = "{}";\n'.format(dtserver.url))
            else:
                new_path.append(l)
    with open(index_path, 'w') as f:
        f.write(''.join(new_path))


def serve_dativetop_gui(old_service, dative_app, dtserver):
    _repair_dativetop_gui_index_html(old_service, dative_app, dtserver)
    return dtutils.Service(
        name='DTGUI',
        url=DATIVETOP_GUI_URL,
        stopper=serve_local_js_app('DTGUI', DATIVETOP_GUI_URL, DATIVETOP_GUI_ROOT))

