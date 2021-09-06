================================================================================
  DativeTop: `DativeBase`_ as a Desktop Application
================================================================================

`DativeBase`_ is *web-based* software for linguistic fieldwork. DativeTop is
DativeBase as a *desktop* application. It is `Dative`_ and the `OLD`_ wrapped
in a `Toga`_ and packaged into a `Briefcase`_.

DativeTop is currently a work in progress. When complete, DativeTop will be a
cross-platform (Windows and Mac OS) desktop application that allows users to
have local copies of their Online Linguistic Databases (OLDs). The files of
these OLDs will be saved to the local filesystem and their structured data will
be saved to local SQLite files. DativeTop provides a graphical interface to
allow users to create new local OLDs and configure them to be read-only replicas
of remote "parent" OLDs. In phase 2, DativeTop will allow the local OLDs to be
mutable and will support synchronization and conflict resolution between local
and remote OLDs.


Install
================================================================================

End users will ultimately be able to install DativeTop in a way that is familiar
on their platform. For example, Mac OS users will be able to download a
DativeTop.dmg package, double-click it, drag the DativeTop.app folder to their
Applications folder, and double-click DativeTop.app to start a running DativeTop
that just works.

However, DativeTop is not there yet. In the meantime, if you are feeling
adventurous, you can try to install DativeTop's dependencies and either run it
in development mode or build the native binaries yourself using the
instructions in the sections that follow.


Install from Source
================================================================================

The following instructions should install DativeTop on Unix-based systems, i.e.,
Mac OS or Linux.

Activate a Python 3 virtual environment (creating it first with ``python -m
venv venv`` if needed)::

    $ source venv/bin/activate

Making sure you are in the directory containing this file, clone the Dative and
OLD submodules using the following git command::

    $ git submodule update --init --recursive

Extract the pre-built Dative (JavaScript) source to ``src/dative/dist/``::

    $ rm -rf src/dative/dist/
    $ cd src/dative/releases/
    $ tar -zxvf release-315b7d9a8e2106612639caf13189eb2de8586278.tar.gz
    $ cp -r dist ./../
    $ cd ../..

Install DativeTop's (i.e., the Toga/Briefcase app's) Python dependencies::

    $ pip install -r requirements.txt

Install the OLD's requirements and the OLD itself in development mode::

    $ pip install -r src/old/requirements/testsqlite.txt
    $ pip install -e src/old/

Install DativeTop Server's Python dependencies::

    $ pip install -e src/dativetop/server/

Create a fresh SQLite db for DativeTop Server::

    $ make refresh-dtserver

Build the DativeTop GUI. If successful, the DTGUI re-frame (ClojureScript) app
will be built under src/dativetop/gui/target/.::

    $ cd src/dativetop/gui
    $ npm install -g shadow-cljs
    $ yarn
    $ make build
    $ cd ../../..

At this point, if all of the above was successful, you should be able to start
DativeTop in development mode with the following::

    $ briefcase dev

For details on how to use DativeTop, see the :ref:`Using DativeTop` section.


Install on Windows
--------------------------------------------------------------------------------

Installation on Windows is similar to that on Mac (Unix). First, install Git and
Python 3.6 using the pre-built installers available on GitHub. Then open
PowerShell and run the following commands.

**WARNING: these instructions are currently incomplete.**

Create a dev directory if you do not have one already::

    > cd ~
    > mkdir Development
    > cd Development

Clone the DativeTop source code, check out the current dev branch, and clone the submodules::

    > git clone https://github.com/dativebase/dativetop.git
    > cd dativetop
    > git submodule update --init --recursive

Make note of the location of Python and Pip. In my case, given the default
install using the Python .exe installer, they were at::

    > C:\Users\username\AppData\Local\Programs\Python\Python36\python.exe
    > C:\Users\username\AppData\Local\Programs\Python\Python36\Scripts\pip.exe

Create the virtual environment using ``venv``::

    > C:\Users\username\AppData\Local\Programs\Python\Python36\python.exe -m venv C:\Users\username\Development\venv

Activate the venv::

    > cd ~\Development
    > .\venv\Scripts\Activate.ps1

Extract the pre-built Dative and move it to ``src/dative/dist/``::

    > cd dativetop\src\dative\releases
    > tar -zxvf release-315b7d9a8e2106612639caf13189eb2de8586278.tar.gz
    > mv dist ..\dist
    > cd ~\Development\dativetop

Install DativeTop's Python dependencies::

    > pip3 install -r requirements.txt
    > pip3 install -r src/old/requirements/testsqlite.txt
		> pip3 install -e src/old/
		> pip3 install -e src/dativetop/server/

TODO: continue these instructions.


Build a Release
================================================================================

Using Briefcase_, it should be possible to build a production release of
DativeTop locally. Building DativeTop means constructing native application
packages for a particular target platform, e.g., Mac OS X or Windows.

The catch is that you must be on the platform for which you are building. That
is, you can only build a MacOS release on a Mac and a Windows release on Windows.


Build on Mac OS
--------------------------------------------------------------------------------

To build a production release of DativeTop on MacOS run::

    $ make build-macos

The core of the above command is a call to ``briefcase build``. The make command
does a little more work by pruning out some unnecessary files and directories
that are not needed in the DativeTop app.

If successful, your ``.app`` application directory will be at
``macOS/DativeTop/DativeTop.app``. Mac treats these directories as applications.
You should be able to double-click this file in order to run DativeTop.

Once the build has been created under ``macOS/``, you may build a release (.dmg)
file with::

    $ briefcase package --no-sign

If successful, the above will create the versioned .dmg file under the
``macOS/`` directory. You can double-click this file and Finder will display a
volume containing DativeTop where you can drag DativeTop to you Applications
folder to install it, just like any other app.

To clear out all existing OLDs and DativeTop state, use the following
convenience make command::

    $ make refresh-dativetop

The above is useful if you are building DativeTop repeatedly during a debugging,
testing, and/or development scenario.


Build on Windows
--------------------------------------------------------------------------------

TODO.


Troubleshooting
================================================================================

Logs
--------------------------------------------------------------------------------

The logs for DativeTop running in dev mode can be found at::

    src/dativetop.log

The logs of a built DativeTop app can be found (on a Mac) at::

    DativeTop.app/Contents/Resources/app/dativetop.log


Blank Screen
--------------------------------------------------------------------------------

If you launch DativeTop and see a blank screen, it may be that a previous
DativeTop was not shut down correctly. Search for the offending process and
kill it::

    $ ps aux | grep dativetop
    $ someuser       45469   0.0  0.1  4357248  10392 s014  S    10:58am   0:00.12 python -m dativetop
    $ kill 45469
    $ make launch


Pillow (OLD dep) Won't Install
--------------------------------------------------------------------------------

If you run into trouble installing Pillow (an OLD dependency for image
processing), then you might need to install libjpeg and zlib. See:

- https://stackoverflow.com/questions/34631806/fail-during-installation-of-pillow-python-module-in-linux
- https://github.com/python-pillow/Pillow/issues/3438

On Mac OS 10.14 (Mojave), I had to install the zlib headers by manually
installing the macOS SDK headers (YMMV)::

    $ brew install libjpeg zlib
    $ sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /


Viewing Console Output from a Build
--------------------------------------------------------------------------------

Sometimes a built DativeTop is failing mysteriously and inspecting the logs is
insufficient. If you double-click on ``DativeTop.app`` and the application does
not work as expected, you can launch DativeTop manually such that any exceptions
that are raised by the underlying Python code are visible in the terminal::

    $ macOS/DativeTop.app/Contents/MacOS/DativeTop


Developer Conveniences
================================================================================

To view the convenience ``make`` commands that are available::

    $ make help

Note that some of these make commands are no longer applicable and should be
deprecated.


Known issues
================================================================================

File upload does not work on Mac OS X
--------------------------------------------------------------------------------

When you click the "Choose file" button in the "New File" interface, the file
browse menu does not open up. This is a known issue with Toga related to the
Cocoa WebView widget. See the `DativeTop cannot upload files`_ issue on GitHub.

The workaround at present is to open DativeTop's local Dative in a browser and
do your file upload from there. DativeTop makes this easy: click on the "Help"
menu and then click "Visit Dative in Browser".

Note that this issue is really a non-issue in the context of read-only local
OLDs since files cannot be uploaded in such OLDs anyway because they are
read-only. It will become a more significant issue when the read-only
restriction is removed at a later iteration.


Architecture
================================================================================

This section describes each of the components of DativeTop.

- DativeTop Toga App:

  - minimal Toga native GUI components: WebViews, top-level menu items, icons
  - starts and serves local servers for 4 other components: Dative GUI, OLD
    Service, DativeTop Service, DativeTop GUI.

- Dative GUI (a.k.a., Dative App): interface to multiple OLD instances
- OLD Service: serves OLD instances at local URLs
- DativeTop GUI: interface to DativeTop Service
- DativeTop Service: the source of truth on the local OLD instances, the Dative
  App, the OLD Service, and the queue of sync-OLD! commands.
- SyncManager: thread that ensures each auto-syncing OLD has a sync-OLD! command
  when it needs one.
- SyncWorker: thread that performs the auto-syncing of OLDs.


Using DativeTop
================================================================================

When the DativeTop app is running, it should open a platform-native window
displaying the DativeTop GUI. This is where you view your local OLD instances
and create new ones.

To view your local OLDs via the Dative GUI, click View > Dative in DativeTop's
top-level menubar, or use the cmd/ctrl-D shortcut. In order to access the
local OLD, you first have to tell Dative that it exists. From within Dative,
first click on Dative > Application Settings, then click on the Servers button,
and then click the "+" ("create a new server") button. The "Name" of the OLD can
be anything but a good choice is same name as that specified in the DativeTop
GUI when the OLD was created. The "URL" of the OLD must be the URL of the local
OLD server (likely http://127.0.0.1:5679), followed by a forward slash and then
the slug of the OLD, e.g., http://127.0.0.1:5679/aa1.

Once you have created the OLD server within Dative, you will be able to login to
the OLD from Dative as usual. Each instance you create will have the same
username and password:

- username: ``admin``
- password: ``adminA_1``

If you want to auto-sync this OLD with an external OLD, you must enable auto-sync
and also specify the URL, username and password of its remote parent OLD.

- auto-sync?: Click the auto-sync? checkbox to enable automated
  synchronization between this local OLD and its remote (parent) OLD.
- remote OLD URL: Specify the URL of the remote OLD. For example, use
  https://do.onlinelinguisticdatabase.org/blaold to specify the Blackfoot OLD.

  - During development/testing, this may be a local OLD that is being served by a
    separate process, e.g., via the `DativeBase docker-compose local deployment
    strategy`_.
  - Note that the remote OLD must be running a version that supports the
    ``/sync`` endpoint.

- remote OLD username/password: Your credentials that allow you to login to the
  remote OLD.

DativeTop uses DativeTop Server to manage its state in a SQLite database.
If you need to debug the operation of Dativetop, it may be helpful to know that
its database file and its log file can be found at:

- db file: ``src/dativetop/server/dativetop.sqlite``
- log file: ``src/dativetop.log``

Your local OLD instances are all read-only. This means that Dative will allow
you to *try* to update, create and delete entities (e.g., forms), but the
underlying OLD instance will prohibit such actions.

Each local OLD instance has its own SQLite database and filesystem directory.
The names of both of these will be determined by the "slug" of the OLD that you
have specified. For example, if the slug is ``aa1``, then the OLD's database
file and filesystem directory will be found at:

- OLD db file: ``src/old/aa1.sqlite``
- OLD directory: ``src/old/store/aa1/``

When DativeTop is running, both Dative and the OLD will be served locally.
This means that you can access them from a regular web browser (e.g., Chrome,
Firefox, etc.) at the following URLs:

- Dative: http://127.0.0.1:5678/
- The *aa1* OLD instance: http://127.0.0.1:5679/aa1/

When you are running a DativeTop instance that has been built for Mac OS, all of
the paths described above are still valid, except you must replace the ``src``
with ``macOS/DativeTop/DativeTop.app/Contents/Resources/app``. For example, the
DativeTop SQLite database file will be at
``macOS/DativeTop/DativeTop.app/Contents/Resources/app/dativetop/server/dativetop.sqlite``.


.. _`BeeWare`: https://github.com/pybee/beeware
.. _`Briefcase`: https://github.com/pybee/briefcase
.. _`Dative`: https://github.com/dativebase/dative
.. _`DativeBase`: https://github.com/dativebase/dativebase
.. _`DativeBase docker-compose local deployment strategy`: https://github.com/dativebase/dativebase/tree/master/docker-compose
.. _`DativeTop cannot upload files`: https://github.com/dativebase/dativebase/issues/16
.. _`OLD`: https://github.com/dativebase/old-pyramid
.. _`Toga`: https://github.com/pybee/toga
