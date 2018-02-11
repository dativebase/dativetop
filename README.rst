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
- Form browse breaking: can add forms but if you navigate away you can't get
  back.
- You currently have to build the OLD database yourself::

    ``initialize_olddb development.ini``


For Developers
================================================================================

To launch DativeTop make sure you have `Toga`_ installed and run::

    $ cd dativetop
    $ python -m src.Dative.app


.. _`DativeBase`: https://github.com/dativebase/dativebase
.. _`Dative`: https://github.com/dativebase/dative
.. _`Online Linguistic Database (OLD)`: https://github.com/dativebase/old-pyramid
.. _`Toga`: https://github.com/pybee/toga
.. _`Briefcase`: https://github.com/pybee/briefcase
