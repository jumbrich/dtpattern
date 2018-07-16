# -*- coding: utf-8 -*-

"""Console script for dtpattern."""

import click
from dtpattern.unicode_translate.pattern_detection_print import pattern_to_string
from dtpattern.value_pattern_detection import pattern


@click.group()
def dtpattern():
    """dtpattern cli , generate patterns for a set of values"""
    pass

@dtpattern.command()
@click.argument('items', nargs=-1)
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--collpase',  is_flag=True)
def items(items, verbose,collpase):
    """read values from cli"""

    if verbose:
        click.echo("Item list {}".format(items))

    res= pattern(items)

    if verbose:
        click.echo("Result(s):")
    res_str = pattern_to_string(res, collapse_multi=collpase)
    click.echo(" {}".format(res_str))

@dtpattern.command()
@click.argument('file',  type=click.File('r'))
@click.option('-v', '--verbose', count=True)
@click.option('-c', '--collpase',  is_flag=True)
def file(file, verbose, collpase):
    """read values from a file"""

    items=file.read().splitlines()
    if verbose:
        click.echo("Item list {}".format(items))

    res= pattern(items)

    if verbose:
        click.echo("Result(s):")

    res_str=pattern_to_string(res, collapse_multi=collpase)
    click.echo(" {}".format(res_str))



