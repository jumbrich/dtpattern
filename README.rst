=========
dtpattern
=========


.. image:: https://img.shields.io/pypi/v/dtpattern.svg
        :target: https://pypi.python.org/pypi/dtpattern

.. image:: https://img.shields.io/travis/jumbrich/dtpattern.svg
        :target: https://travis-ci.org/jumbrich/dtpattern

.. image:: https://readthedocs.org/projects/dtpattern/badge/?version=latest
        :target: https://dtpattern.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

Installation
============

This module is not yet registered with the Python package index::

If you want the bleeding edge, clone the source code repository::

    $ git clone git@github.com:jumbrich/dtpattern.git
    $ cd dtpattern
    $ python setup.py install

Usage
=====

You can either use the class with the simple CLI interface::

    #>dtpattern 1 2 23
    Result: [('01', 3)]




Notes
=====

The general idea is to get for a list of input values a single representation about their patterns ( characters, numbers, special symbols).
Such patterns, can be later used to
* identify certain data types,
* the structure of the values
* detect ID patterns
* ...


Generate a pattern represenation for a set of values


* Free software: MIT license
* Documentation: https://dtpattern.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
