================================================================================
DativeTop: `DativeBase`_ as a desktop application
================================================================================

`DativeBase`_ is *web-based* software for linguistic fieldwork. DativeTop is
DativeBase as a *desktop* application. It is `Dative`_ and the `OLD`_ wrapped
in a `Toga`_ and packaged into a `Briefcase`_.


Install
================================================================================

End users *should* be able to install DativeTop in a way that is familiar on
their platform. For example, Mac OS users should be able to download a
DativeTop.dmg package, double-click it, drag the DativeTop.app folder to their
Applications folder, and double-click on DativeTop.app to start a running
DativeTop that just works.

But DativeTop is not there yet. In the meantime, if you are feeling
adventurous, you can try to build and run DativeTop on your Mac using the
`Build`_ instructions below.


Build
================================================================================

First, Ensure that you have GNU Make installed by running ``make -v``. Then
create and activate a Python 3.6 (or 3.5) virtual environment::

    $ python3 --version
    Python 3.6.0
    $ python3 -m venv venv
    $ source venv/bin/activate
    (venv) $


Build for Mac OS X
--------------------------------------------------------------------------------

Move into the directory containing this file and run the following command::

    (env) $ make build-mac-os

If the above succeeds, you should have a directory named DativeTop.app under
macOS/. Double-clicking this should open DativeTop, which will display Dative.
You should be able to login to the default *myold* OLD instance with username
*admin* and password *adminA_1*.


Build for Linux and Windows
--------------------------------------------------------------------------------

TODO.


Troubleshooting
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If the above does not work, you can launch DativeTop manually in another way
(besides double-clicking on DativeTop.app) such that any exceptions that are
raised by the underlying Python code are viewable in the terminal::

    (env) $ macOS/DativeTop.app/Contents/MacOS/DativeTop


For Developers
================================================================================

First, create (if necessary) and activate a Python 3.6/5 virtual environment as
explained above.

Then install DativeTop's requirements as well as those of the OLD submodule
and the OLD itself in development mode::

    (venv) $ pip install -r requirements/base.txt -e src/old/

Use the Makefile to see the convenience commands that are available::

    $ make help
    ...

In general, you will want to build Dative, create an OLD instance, and then
launch DativeTop::

    $ make build-dative
    $ make create-old-instance OLD_NAME=myold
    $ make launch

Note: the ``create-old-instance`` command will create a SQLite database file in
``oldinstances/dbs/`` as well as a directory for your OLD instance's files in
``oldinstances/``. The corresponding "undo" command, which destroys an OLD
instance's database and directory structure, is ``destroy-old-instance``.

DativeTop should open a window (WebView) wherein Dative is running. You should
now be able to login to the OLD named ``myold`` from the Dative interface using
username *admin* and password *adminA_1*. Note that Dative and the OLD will be
being served locally so you can view them in a regular browser at the following
URLs:

- Dative: http://127.0.0.1:5678/
- The *myold* OLD instance: http://127.0.0.1:5679/myold/


Troubleshooting
--------------------------------------------------------------------------------

If you launch DativeTop and see a blank screen, it may be that a previous
DativeTop was not shut down correctly. Search for the offending process and
kill it::

    $ ps aux | grep dativetop
    $ someuser       45469   0.0  0.1  4357248  10392 s014  S    10:58am   0:00.12 python -m dativetop
    $ kill 45469
    $ make launch


Known issues
================================================================================

- File upload does not work. When you click the "Choose file" button in the
  "New File" interface, the file browse menu does not open up.


.. _`DativeBase`: https://github.com/dativebase/dativebase
.. _`Dative`: https://github.com/dativebase/dative
.. _`OLD`: https://github.com/dativebase/old-pyramid
.. _`Toga`: https://github.com/pybee/toga
.. _`Briefcase`: https://github.com/pybee/briefcase
