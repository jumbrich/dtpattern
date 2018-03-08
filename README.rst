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

DTPattern, a pattern language for a set of values ( think in terms of regular expressions)

        * Free software: MIT license
        * Documentation: https://dtpattern.readthedocs.io.

Notes
=====

The general idea is to get for a list of input values a single representation about their patterns ( characters, numbers, special symbols).
Such patterns, can be later used to

* identify certain data types,
* the structure of the values
* detect ID patterns
* ...


Installation
============

This module is not yet registered with the Python package index::

If you want the bleeding edge, clone the source code repository::

    $ git clone git@github.com:jumbrich/dtpattern.git
    $ cd dtpattern
    $ python setup.py install

Usage
=====

You can either use the class with the simple CLI interface
read values from command line::

    #>dtpattern items 1 23 123
    ('001', 3)
    #>dtpattern items 1 23 123 --raw
    001

Read from a file::

    #>dtpattern file tests/dates_list.txt
      ('11/11/1111 11:11:11 CC', 5)

Use dtpattern in your code::

    from dtpattern.dtpattern import pattern

    items=['123','123','123']
    res= pattern(items)


Pattern language
====

To generate the pattern we first apply the following mapping:


==== ====
Input character Mapping
-------------------- ------
[A-Z,ÄÜÖ]             A or C as placholder

[a-z,äüö]            a or c as placholder
[0-9]                 1 or 0 as placeholder
!"#$%&*<=>?@|         $
()[]{}                ß
==== ====

Note, the mapping can be adjusted in the dtpattern.py class

Next, we try to group the input values by their pattern representation and do this at different aggregation levels:

**Level1**: We group the input patterns  (no aggregation). If all values adhere to the same pattern and length, the algorithm would already terminate::

  #>dtpattern items 1010 1011 1012 --raw --verbose
    Item list ('1010', '1011', '1012')
    L1: 1 groups, [('1111', 3)]
    Result(s):
    1111

**Level2**: In level 2, we group patterns by their unique oder of distinct pattern symbols and afterwards aggregate such groups::

  #>dtpattern items 1010-AT 1011-AT 101-AT --raw --verbose
  Item list ('1010-AT', '1011-AT', '101-AT')
    L1: 2 groups, [('111-CC', 1), ('1111-CC', 2)]
     L2: 1 groups, [('1-C', 2, [('111-CC', 1), ('1111-CC', 2)])]
     > [['111', '1111'], ['-', '-'], ['CC', 'CC']]
     < 0111-CC
  Result(s):
   0111-CC

In this example, we see that the patterns have the unique symbol sequence 1-C and as a result we aggregate first the number group , then - and then the upper characters.

The resulting pattern is **0111-CC**, meaning:

* **0111** that there are at least 3 numbers (some values have 4, indicated by the leading 0), followed by
* **-** and
* **CC** two upper case characters

**TODO**: Add more documentation for the third  aggregation level, explaining thresholds and how values with non unique symbol sequences are represented.

More examples::

  #>dtpattern items 1010-AT 1011-AT 101-AT AT-1210 --raw --verbose
  Item list ('1010-AT', '1011-AT', '101-AT', 'AT-1210')
   L1: 3 groups, [('111-CC', 1), ('1111-CC', 2), ('CC-1111', 1)]
    L2: 2 groups, [('1-C', 2, [('111-CC', 1), ('1111-CC', 2)]), ('C-1', 1, [('CC-1111', 1)])]
     L3 L2:[('1-C', 2, [('111-CC', 1), ('1111-CC', 2)]), ('C-1', 1, [('CC-1111', 1)])]
      aggregating b'C',['1-C', 'C-1']
     -0- K:'C'
      -0- PP ['111-', '1111-']
      -0- PS ['-1111']
      L1: 2 groups, [('111-', 1), ('1111-', 1)]
       L2: 1 groups, [('1-', 2, [('111-', 1), ('1111-', 1)])]
       > [['111', '1111'], ['-', '-']]
       < 0111-
      L1: 1 groups, [('-1111', 1)]
      -0- agg_p_prefix [('0111-', 2)]
      -0- agg_p_suffix [('-1111', 1)]
  Result(s):
  [0111-]CC[-1111]

The resulting pattern **[0111-]CC[-1111]** indicates that we have a common pattern sequence in all input values, which is the two upper case characters **AT**.
The values can either have some leading or trailing number sequence. If leading, the sequence is **0111-**, if trailing, it is **-1111**


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
