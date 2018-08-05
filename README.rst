================================================================================
DativeTop: `DativeBase`_ as a desktop application
================================================================================

`DativeBase`_ (`Dative`_ + the `Online Linguistic Database (OLD)`_) is
server-side software for linguistic fieldwork. DativeTop is the DativeBase as a
desktop application. It is the Dative and the OLD wrapped in a `Toga`_ and
packaged into a `Briefcase`_.


Current Issues
================================================================================

- File upload doesn't work: no file browse menu opens up (Toga->Cocoa issue?)
- Keyboard copy/paste doesn't work

  - Apparently, "On OS X you have to explicitly add menu items for Copy/Paste
    to make them work". See https://github.com/electron/electron/issues/2308.

- Form browse breaking: can add forms but if you navigate away you can't get
  back.
- You currently have to build the OLD database yourself::

    ``initialize_olddb development.ini``


Build and install
================================================================================

First, Ensure that you have GNU Make installed by running ``make -v``. Then,
create and activate a Python 3.6 (or 3.5) virtual environment::

    $ python3 --version
    Python 3.6.0
    $ python3 -m venv venv
    $ source venv/bin/activate
    (venv) $


Build for Mac OS X
--------------------------------------------------------------------------------

From the command line (terminal), change to the directory containing this file
and run the following command::

    (env) $ make build-mac-os

If the above succeeds, you should have a directory named DativeTop.app under
macOS/. Double-clicking this should open up DativeTop which will display
Dative. You should be able to login to the "evermore" OLD with username "admin"
and password "admin_A1".


Troubleshooting
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If the above does not work, you can launch DativeTop manually in another way
(besides double-clicking on DativeTop.app) such that any exceptions that are
raised by the underlying Python code are viewable in the terminal. Run this
command in the terminal::

    (env) $ macOS/DativeTop.app/Contents/MacOS/DativeTop


For Developers
================================================================================

First, create (if necessary) and activate a Python 3.6/5 virtual environment as
explained above.

Then install the DativeTop's requirements as well as those of the OLD submodule
and the OLD itself in development mode::

    (venv) $ pip install -r requirements/base.txt -e src/old/

Use the Makefile to see the convenience commands that are available::

    $ make help
    build-dative                   Build Dative: install NPM dependencies, compile/minify JS and reset its servers array
    build-mac-os                   Build a DativeTop .app bundle for Mac OS
    create-old-instance            Create an OLD instance named OLD_NAME: create a directory structure for it, an SQLite database with tables pre-populated, and register it with Dative
    destroy-old-instance           Destroy OLD instance OLD_NAME's files on disk and its SQLite database and de-register it from Dative
    help                           Print this help message.
    launch                         Launch DativeTop in development mode
    run-mac-os                     Build and run DativeTop .app bundle for Mac OS

In general, you will want to build Dative, create an OLD instance, and then
launch DativeTop::

    $ make build-dative
    $ make create-old-instance OLD_NAME=myold
    $ make launch

DativeTop should open a window (WebView) wherein Dative is running. You should
now be able to login to the OLD named ``myold`` from the Dative interface.


Troubleshooting
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    $ ps aux | grep dativetop
joeldunham       34820   0.0  0.0  4267768    900 s014  S+    2:15pm   0:00.00 grep dativetop
joeldunham       34807   0.0  0.1  4356224   9640 s014  S     2:12pm   0:00.04 python -m dativetop
joeldunham       34798   0.0  0.2  4355680  32076 s001  S+    2:11pm   0:00.93 vim dativetop/app.py


.. _`DativeBase`: https://github.com/dativebase/dativebase
.. _`Dative`: https://github.com/dativebase/dative
.. _`Online Linguistic Database (OLD)`: https://github.com/dativebase/old-pyramid
.. _`Toga`: https://github.com/pybee/toga
.. _`Briefcase`: https://github.com/pybee/briefcase
