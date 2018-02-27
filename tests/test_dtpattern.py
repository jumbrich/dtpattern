#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `dtpattern` package."""


import unittest
from click.testing import CliRunner

from dtpattern import dtpattern
from dtpattern import cli
from dtpattern.dtpattern import pattern


class TestDtpattern(unittest.TestCase):
    """Tests for `dtpattern` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test__something(self):
        """Test something."""
        examples = [
            # ['1','2','3','4','5','6',' '],
            # ['-1', '+2', '-3', '4', '5', '6','-'],
            # ['-1', '+2', '-3', '4', '5', '6'],
            # ['Tim Tom', 'Ulf Uls', 'Max Maxi', 'Alf Also', 'C. A. Term', '123']
            # make_pattern(10, fake.isbn10, separator='-'),
            # make_pattern(10000, fake.uri)
            # ['-1'] + random_number(5, digits=1, fix_len=True)
            # ['-1', '+1'] + random_number(5, digits=1, fix_len=True)
            # [fake.sentence(nb_words=6, variable_nb_words=True) for i in range(0,10)]
            [u'43,462.33', u'30,166.00', u'35,618.00', u'38,356.90', u'77,764.00', u'106,421.00', u'385,895.25',
             u'503,625.00', u'34,122.08', u'127,974.00', u'148,184.64', u'44,832.91', u'30,702.85', u'365,172.00',
             u'92,107.78', u'33,589.13', u'5,448,814.11', u'496,835.21', u'34,170.00', u'449,064.18', u'1,250,000.00',
             u'462,084.00', u'110,777.00', u'33,470.37', u'46,992.13', u'36,000.00', u'32,696.00', u'28,995.06',
             u'68,691.00', u'25,645.77', u'113,913.43', u'106,228.20', u'34,055.72', u'27,809.00', u'137,004.08',
             u'31,531.00', u'38,171.08', u'97,616.70', u'-3,389,597.00']
        ]

        for values in examples:
            print("{}\n V: {}".format("=" * 80, values))
            # p=translate_all(values, filter_empty=False)
            # p = sorted(p, key=functools.cmp_to_key(pattern_comparator))
            # print " {}\n P: {}".format("-" * 80,p)
            # l1=l1_aggregate(p)
            # print "  {}\n   L1: {}".format("." * 80, l1)
            # l2 = l2_aggregate(patterns=p)
            # print "   {}\n   L2: {}".format("'" * 80, l2)
            # l3 = l3_aggregate(l2)
            # print "   {}\n   L3: {}".format("'" * 80, l3)
            a = pattern(values, size=3,verbose=True )
            print("   {}\n  A: {}".format("'" * 80, a))

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'dtpattern.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
