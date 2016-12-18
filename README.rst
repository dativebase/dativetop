================================================================================
Dative Toga
================================================================================

This is a Toga project for Dative and the OLD.

It is under development, but the goal is to package the Dative Backbone.js GUI
app and the OLD Pylons REST API into an offline application controlled via a
simple Toga wrapping and bundled using Briefcase.


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

To launch Dative-Toga, make sure you have `Toga`_ installed and run::

    $ cd dative-toga
    $ python -m src.Dative.app

.. _`Toga`: https://github.com/pybee/toga

