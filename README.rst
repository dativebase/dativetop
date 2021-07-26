================================================================================
  DativeTop: `DativeBase`_ as a Desktop Application
================================================================================


`DativeBase`_ is *web-based* software for linguistic fieldwork. DativeTop is
DativeBase as a *desktop* application. It is `Dative`_ and the `OLD`_ wrapped
in a `Toga`_ and packaged into a `Briefcase`_.

The ultimate goal is for DativeTop to be a desktop application with an icon
that can be double-clicked and just starts up in the manner that is typical for
the platform on which it is being run. DativeTop will save files to the user's
filesystem and structured data to local SQLite files. DativeTop should have an
interface that allows users to configure a local OLD as a subscriber to a
specified OLD instance on the web. DativeTop will have logic for maintaining
consistency with the server-side "leader" OLD.


Install
================================================================================

End users *should* be able to install DativeTop in a way that is familiar on
their platform. For example, Mac OS users should be able to download a
DativeTop.dmg package, double-click it, drag the DativeTop.app folder to their
Applications folder, and double-click on DativeTop.app to start a running
DativeTop that just works.

But DativeTop is not there yet. In the meantime, if you are feeling
adventurous, you can try to install DativeTop's dependencies and either run it
in development mode or build the native binaries yourself using the
instructions in the sections that follow.


Install from Source (for Developers)
================================================================================

QuickStart
--------------------------------------------------------------------------------

For quick reference, here are the core development install commands. Use the
detailed instructions below if this is your first time installing DativeTop
from source::

    $ python3 -m venv venv
    $ source venv/bin/activate
    $ git submodule update --init --recursive
    $ make build-dative
    $ make install
    $ make create-old-instance OLD_NAME=myold
    $ make launch

To install all of the required dependencies manually::

    $ pip install -r requirements.txt && \
		$ pip install -r src/old/requirements/testsqlite.txt && \
		$ pip install -e src/old/ && \
		$ pip install -e src/dativetop/server/ && \
		$ pip install requirements/wheels/dativetop_append_only_log_domain_model-0.0.1-py3-none-any.whl

This command may be useful::

	  $ initialize_old src/old/config.ini myold


Detailed Source Install
--------------------------------------------------------------------------------

Detailed MacOS Source Install
````````````````````````````````````````````````````````````````````````````````

The following instructions should install DativeTop on Mac OS.

Activate a Python 3.6 virtual environment (creating it first with ``python -m
venv venv`` if needed)::

    $ source ../venv3.6.5/bin/activate.fish
    (venv) $

Making sure you are in the directory containing this file, clone the Dative and
OLD submodules using the following git command::

Extract the pre-built Dative (JavaScript) source to ``src/dative/dist/``::

    $ rm -rf src/dative/dist/
    $ cd src/dative/releases/
    $ tar -zxvf release-2c18bdf158fc8664404e67e5530b9a95a18d6d11.tar.gz
    $ cp -r release-9e40102c7fa79618964df7ac9a0a370cc60ee9bd ./../dist
    $ cd ../../..

Install DativeTop's (the Toga/Briefcase app's) Python dependencies::

    (venv3.6.5)$ pip install -r requirements.txt

.. warning:: At present (2021-01-31), Toga's WebView does not accept keyboard
   input. To resolve this, you must manually modify
   venv3.6.5/lib/python3.6/site-packages/toga_cocoa/widgets/webview.py by adding
   the following import and modifying the referenced method as shown below::

       from rubicon.objc import objc_method, py_from_ns, send_super
       @objc_method
       def keyDown_(self, event) -> None:
           if self.interface.on_key_down:
               self.interface.on_key_down(self.interface, **toga_key(event))
           send_super(__class__, self, 'keyDown:', event)

Install the OLD's requirements and the OLD itself in development mode::

    (venv3.6.5)$ pip install -r src/old/requirements/testsqlite.txt
    (venv3.6.5)$ pip install -e src/old/

Install the DativeTop Server's Python dependencies::

    (venv3.6.5)$ pip install -e src/dativetop/server/
		(venv3.6.5)$ pip install requirements/wheels/dativetop_append_only_log_domain_model-0.0.1-py3-none-any.whl

Create the filesystem structure and (SQLite) database for a local OLD named
"myold"::

    (venv3.6.5)$ make create-old-instance OLD_NAME=myold

The above command will create the OLD's SQLite file and its filesystem
structure under ``./oldinstances/``:

- SQLite database file: ``oldinstances/dbs/myold.sqlite``
- OLD directory for saving, e.g., audio, files: ``oldinstances/myold/``

The SQLite db can be accessed as follows::

    (venv)$ sqlite3 oldinstances/dbs/myold.sqlite

The ``create-old-instance`` command above tells Dative about the new OLD by
adding an object to the array defined in::

    src/dative/dist/servers.json

The ``create-old-instance`` command also tells Dative that there is an OLD
instance being served, in this case, at http://127.0.0.1:5679/myold/.

You should now be able to launch DativeTop with the following command::

    $ briefcase dev

TODO: return here. The DativeTop launched via the above is not yet at basic
functionality.

The above command should open DativeTop in a native window for your platform.
That window will display a WebView wherein Dative should be running. You should
be able to login to the OLD named ``myold`` from the Dative interface using
username *admin* and password *adminA_1*. Note that Dative and the OLD will be
being served locally so you can view them in a regular browser at the following
URLs:

- Dative: http://127.0.0.1:5678/
- The *myold* OLD instance: http://127.0.0.1:5679/myold/


Troubleshooting
--------------------------------------------------------------------------------

Blank Screen
````````````````````````````````````````````````````````````````````````````````

If you launch DativeTop and see a blank screen, it may be that a previous
DativeTop was not shut down correctly. Search for the offending process and
kill it::

    $ ps aux | grep dativetop
    $ someuser       45469   0.0  0.1  4357248  10392 s014  S    10:58am   0:00.12 python -m dativetop
    $ kill 45469
    $ make launch


Pillow (OLD dep) Won't Install
````````````````````````````````````````````````````````````````````````````````

If you run into trouble installing Pillow (an OLD dependency for image
processing), then you might need to install libjpeg and zlib. See:

- https://stackoverflow.com/questions/34631806/fail-during-installation-of-pillow-python-module-in-linux
- https://github.com/python-pillow/Pillow/issues/3438

On Mac OS 10.14 (Mojave), I had to install the zlib headers by manually
installing the macOS SDK headers (YMMV)::

    $ brew install libjpeg zlib
    $ sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /


Developer Hints
--------------------------------------------------------------------------------

To view the convenience ``make`` commands that are available::

    $ make help

In a typical development workflow, you will want to build Dative, create an OLD
instance, and then launch DativeTop using the following commands::

    $ make build-dative
    $ make create-old-instance OLD_NAME=myold
    $ make launch

Note: the ``create-old-instance`` command will create a SQLite database file in
``oldinstances/dbs/`` as well as a directory for your OLD instance's files in
``oldinstances/``. The corresponding "undo" command, which destroys an OLD
instance's database and directory structure, is ``destroy-old-instance``.


Build
================================================================================

Building DativeTop means constructing native application packages for a
particular target platform, e.g., Mac OS X or Windows.


Build for Mac OS X
--------------------------------------------------------------------------------

To build the DativeTop.app MacOS artifact, run the following on a Mac::

    $ briefcase build

To clear out all existing OLDs and DativeTop state, use the following
convenience make command::

    $ make refresh-dativetop


Potentially Deprecated MacOS Build Commands
````````````````````````````````````````````````````````````````````````````````

Previous ``beeware-build-mac-os`` command::

    DFLT_DATIVETOP_OLD_NAME=${DFLT_DATIVETOP_OLD_NAME} beeware build macOS

New ``beeware-build-mac-os`` command::

    DFLT_DATIVETOP_OLD_NAME=${DFLT_DATIVETOP_OLD_NAME} python setup.py macos -s

Run the following command::

    (venv) $ make build-mac-os

If the above succeeds, you should have a directory named DativeTop.app under
macOS/. Double-clicking this should open DativeTop, which will display Dative.
You should be able to login to the default *myold* OLD instance with username
*admin* and password *adminA_1*.

To build a mountable disk image containing DativeTop.app (i.e., a DMG file)::

    (venv) $ make release-mac-os


Troubleshooting
````````````````````````````````````````````````````````````````````````````````

If you double-click on DativeTop.app and the application does not work as
expected, you can launch DativeTop manually such that any exceptions that are
raised by the underlying Python code are viewable in the terminal::

    (venv) $ macOS/DativeTop.app/Contents/MacOS/DativeTop


Build for Linux and Windows
--------------------------------------------------------------------------------

TODO.


Known issues
================================================================================

File upload does not work on Mac OS X
--------------------------------------------------------------------------------

When you click the "Choose file" button in the "New File" interface, the file
browse menu does not open up.  This is a known issue with Toga related to the
Cocoa WebView widget. See the `DativeTop cannot upload files`_ issue on GitHub.

The workaround at present is to open DativeTop's local Dative in a browser and
do your file upload from there. DativeTop makes this easy: click on the "Help"
menu and then click "Visit Dative in Browser".


Architecture
================================================================================

- DativeTop Toga App:

  - minimal Toga native GUI components: WebViews, top-level menu items, icons
  - starts and serves local servers for 4 other components: Dative GUI, OLD
    Service, DativeTop Service, DativeTop GUI.

- Dative GUI: interface to multiple OLD instances

- OLD Service: serves OLD instances at local URLs

- DativeTop GUI: interface to DativeTop Service

- DativeTop Service: manages local OLD instances, syncs them to external
  leaders, ...


Notes and Possible Issues
================================================================================

Warning seemingly from Mac OS:

    2020-07-30 11:14:23.303 python[45386:5039192] *** WARNING: Method convertPointToBase: in class NSView is deprecated on 10.7 and later. It should not be used in new applications.


Build on Windows
================================================================================

Strategy 1: Use an Azure Windows Server 2019 Free Instance (2020-10)
--------------------------------------------------------------------------------

First, install Git and Python 3.6 using the pre-built installers available on
GitHub. Then open PowerShell and run the following commands.

Create a dev directory if you do not have one already::

    > cd ~
    > mkdir Development
    > cd Development

Clone the DativeTop source code, check out the current dev branch, and clone the submodules::

    > git clone https://github.com/dativebase/dativetop.git
    > cd dativetop
    > git fetch origin -a
    > git checkout -b dev/build-on-windows origin/dev/build-on-windows
    > git submodule update --init --recursive

Make note of the location of Python and Pip. In my case, given the default
install using the Python .exe installer, they were at::

    > C:\Users\jrwdunham\AppData\Local\Programs\Python\Python36\python.exe
    > C:\Users\jrwdunham\AppData\Local\Programs\Python\Python36\Scripts\pip.exe

Create the virtual environment using ``venv``::

    > C:\Users\jrwdunham\AppData\Local\Programs\Python\Python36\python.exe -m venv C:\Users\jrwdunham\Development\venv

Activate the venv::

    > cd ~\Development
    > .\venv\Scripts\Activate.ps1
    (venv)>

Extract the pre-build Dative and move it to ``src/dative/dist/``::

    (venv)> cd dativetop\src\dative\releases
    (venv)> tar -xvzf release-2c18bdf158fc8664404e67e5530b9a95a18d6d11.tar.gz
    (venv)> mv release-2c18bdf158fc8664404e67e5530b9a95a18d6d11 ..\dist
    (venv)> cd ~\Development\dativetop

Install DativeTop's Python dependencies::

    (venv)> pip3 install -r requirements.txt
    (venv)> pip3 install -r src/old/requirements/testsqlite.txt
		(venv)> pip3 install -e src/old/
		(venv)> pip3 install -e src/dativetop/server/
		(venv)> pip3 install requirements/wheels/dativetop_append_only_log_domain_model-0.0.1-py3-none-any.whl

Initialize an OLD named ``testold``::

    (venv)> initialize_old src\old\configlocal.ini myold

Launch DativeTop::

.. _`DativeTop cannot upload files`: https://github.com/dativebase/dativebase/issues/16
.. _`DativeBase`: https://github.com/dativebase/dativebase
.. _`Dative`: https://github.com/dativebase/dative
.. _`OLD`: https://github.com/dativebase/old-pyramid
.. _`BeeWare`: https://github.com/pybee/beeware
.. _`Toga`: https://github.com/pybee/toga
.. _`Briefcase`: https://github.com/pybee/briefcase
