================================================================================
DativeTop: `DativeBase`_ as a desktop application
================================================================================

pip install --upgrade --force-reinstall --process-dependency-links --target=/Users/joeldunham/Development/dativetop/dativetop/macOS/DativeTop.app/Contents/Resources/app_packages old

`DativeBase`_ (`Dative`_ + the `Online Linguistic Database (OLD)`_) is
server-side software for linguistic fieldwork. DativeTop is the DativeBase as a
desktop application. It is the Dative and the OLD wrapped in a `Toga`_ and
packaged into a `Briefcase`_.


Current Issues
================================================================================

- File upload doesn't work: no file browse menu opens up (Toga->Cocoa issue?)
- Keyboard copy/paste doesn't work
- Form browse breaking: can add forms but if you navigate away you can't get
  back.
- You currently have to build the OLD database yourself::

    ``initialize_olddb development.ini``


For Developers
================================================================================

Create and activate a Python 3.6 virtual environment::

    $ python3 --version
    Python 3.6.0
    $ python3 -m venv venv
    $ source venv/bin/activate
    (venv) $

Install the requirements, including those of the OLD submodule::

    (venv) $ pip install -r requirements/base.txt -e src/old/

To launch DativeTop, from the same directory with setup.py in it, run::

    $ python -m dativetop


.. _`DativeBase`: https://github.com/dativebase/dativebase
.. _`Dative`: https://github.com/dativebase/dative
.. _`Online Linguistic Database (OLD)`: https://github.com/dativebase/old-pyramid
.. _`Toga`: https://github.com/pybee/toga
.. _`Briefcase`: https://github.com/pybee/briefcase
