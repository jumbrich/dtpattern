# -*- coding: utf-8 -*-

"""Console script for dtpattern."""

import click
from csvmimesis.mimesis_data_providers import list_locals, list_providers_methods
from csvmimesis.table_generator import create_data_provider_list
from dtpattern import value_pattern_detection
from dtpattern.unicode_translate.pattern_detection_print import pattern_to_string
from dtpattern.unicode_translate.translate import higher_level
from dtpattern.unicode_translate.unicode_categories import A, CAT

from dtpattern.value_pattern_detection import pattern, uc_agg, pf
from pyjuhelpers.string_format import print_columns
from pyjuhelpers.timer import Timer



@click.group()
def ucs():
    """Show availabe unicode categories"""
    pass

@ucs.command()
def ucs():
    """show unicode categories with 10 example values"""
    print(A.print(ex=CAT))
