================================================================================
DativeTop: `DativeBase`_ as a desktop application
================================================================================

`DativeBase`_ (`Dative`_ + the `Online Linguistic Database (OLD)`_) is
server-side software for linguistic fieldwork. DativeTop is the DativeBase as a
desktop application. It is the Dative and the OLD wrapped in a `Toga`_ and
packaged into a `Briefcase`_.


Usage
================================================================================

The purpose of DativeTop is to make it easy for a non-technical end user to
install and launch DativeBase on their desktop machine. Therefore, you should
not need to know about the command line in order to use DativeTop. You should
be able to just download a .app file or .exe file and double-click it. We are
still working on getting to this stage. Please check back here later.

If you are feeling adventurous and would like to try to build DativeTop on Mac
OS X, then proceed to the instructions below. (Support for other platforms will
be forthcoming.)


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
now be able to login to the OLD named ``myold`` from the Dative interface using
the default administrator user that the OLD creates by default:

- username: admin
- password: adminA_1

Note that Dative and your OLD instance will now be being served locally on the
following two URLs. You should be able to interact with these from a regular
browser as well as via DativeTop:

- Dative: http://127.0.0.1:5678/
- OLD instance: http://127.0.0.1:5679/myold/


Troubleshooting
--------------------------------------------------------------------------------

Blank screen
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If DativeTop opens with a blank white screen, the previous process may not have
shut down properly. If applicable, search for that process and kill it::

    $ ps aux | grep dativetop
    someuser       34807   0.0  0.1  4356224   9640 s014  S     2:12pm   0:00.04 python -m dativetop
    $ kill 34807


OLD instances not visible in Dative
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

DativeTop may not display the OLD that you created (with
``make create-old-instance OLD_NAME=myold`` above) in its login interface. This
is because Dative's known OLDs are stored in the WebView's LocalStorage and
DativeTop does not know how to clear that cache. The solution is to create a
"server" within DativeTop's Dative interface that corresponds to the OLD
instance that you created:

1. Click on "Application Settings" under the "Dative" menu.
2. Click on the "Servers" button.
3. Open the "create a new server" interface by clicking on the "+" button.
4. In the "Name" field, enter the name of your OLD instance, e.g., "myold".
5. In the "URL" field, enter ``http://127.0.0.1:5679/<old_instance_name>``, e.g.,
   ``http://127.0.0.1:5679/myold`` if you named your OLD instance ``myold``
   when you ran ``make create-old-instance`` above.

After doing the above, you should be able to login to your OLD instance from
DativeTop.


Known Issues
================================================================================

- File upload does not work. If you click on "Resources", then "Files" and then
  the "+" button to create a new file entity, and then click the "Choose file"
  button, nothing will happen.

- Keyboard copy/paste does not work. Apparently, "On OS X you have to
  explicitly add menu items for Copy/Paste to make them work"; see
  https://github.com/electron/electron/issues/2308.

- Building DativeTop on Mac OS X results in a .app bundle that does not have
  the OLD icon.


.. _`DativeBase`: https://github.com/dativebase/dativebase
.. _`Dative`: https://github.com/dativebase/dative
.. _`Online Linguistic Database (OLD)`: https://github.com/dativebase/old-pyramid
.. _`Toga`: https://github.com/pybee/toga
.. _`Briefcase`: https://github.com/pybee/briefcase
