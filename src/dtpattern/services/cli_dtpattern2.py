# -*- coding: utf-8 -*-

"""Console script for dtpattern."""
import sys
import click
from csvmimesis.mimesis_data_providers import list_locals, list_providers_methods
from csvmimesis.table_generator import create_data_provider_list

from dtpattern.dtpattern2 import PatternFinder
from dtpattern.alignment.alignment_cls import Alignment
from dtpattern.alignment.pattern_cls import Pattern
from pyjuhelpers.string_format import print_columns
from pyjuhelpers.timer import Timer
from dtpattern.dtpattern2 import pattern as pattern2


@click.group()
def dtpattern2():
    """dtpattern cli , generate patterns for a set of values"""
    pass

@dtpattern2.command()
@click.argument('s1', nargs=1)
@click.argument('s2', nargs=1)
@click.option('--m', type=int, default=5)
@click.option('--mm', type=int, default=-4)
@click.option('--om', type=int, default=3)
@click.option('--csetm', type=int, default=4)
@click.option('--go', type=int, default=-15)
@click.option('--ge', type=int, default=-1)


def alignpair(s1, s2, verbose,  m, mm, go, ge, om, csetm):
    click.echo("INPUT s1: {}".format(s1))
    click.echo("INPUT s2: {}".format(s2))
    s1,s2 = [ c for c in s1], [ c for c in s2]

    a= Alignment(Pattern(s1),Pattern(s2),  m=m, mm=mm, om=om, csetm=csetm,go=go, ge=ge)
    click.echo(a)


@dtpattern2.command()
@click.argument('items', nargs=-1)
@click.option('--size', type=int, default=1)
@click.option('-v', '--verbose', count=True)
def items(items,size, verbose):

    if verbose:
        click.echo("Item list {}".format(items[0:10]))
    pm = PatternFinder(max_pattern=size)
    for value in items:
        pm.add(value)
    if verbose:
        click.echo("Time elapsed {} ms for {} values".format(t.elapsed, len(items)))
        click.echo(repr(pm))
    else:
        click.echo(pm.info())

@dtpattern2.command()
@click.argument('file',  type=click.File('r'))
@click.option('--size', type=int, default=1)
@click.option('-v', '--verbose', count=True)
def file(file, verbose,  size):
    """read values from a file"""

    items = file.read().splitlines()
    if verbose:
        click.echo("Item list {}".format(items[0:10]))

    pm = PatternFinder(max_pattern=size)
    c=0
    for value in file:
        pm.add(value)
        c+=1

    if verbose:
        click.echo("Time elapsed {} ms for {} values".format(t.elapsed, c))
        click.echo(repr(pm))
    else:
        click.echo(pm.info())


##### DEMO #####

def datagenerator(local=None, provider=None, method=None, size=10, seed="ascd"):
    for l in list_locals():
        if not local or l == local:

            for pm in list_providers_methods(local=l, max_unqiue=size, only_max=False, seed=seed,provider=provider, method=method):
                p = "{}.{}".format(pm[0], pm[1])
                key = "{}-{}".format(l, p)
                try:
                    header, data = create_data_provider_list(providers=[["{}".format(p)]], size=size, local=l, seed=seed)

                    data = data[header[0]]
                    if isinstance(data[0], list) or isinstance(data[0], tuple) or isinstance(data[0], set) or isinstance(data[0], dict):
                        continue
                    data = [str(d) for d in data]

                    yield key,data
                except Exception as e:
                    print("Someing wrrong",e)

@dtpattern2.command('demo')
@click.option('-s', '--size', type=int, default=10)
@click.option('-p', '--provider', type=str, default=None)
@click.option('-m', '--method', type=str, default=None)
@click.option('-g', '--groups', type=int, default=2)
@click.option('-l', '--local', type=str, default="en")
def demo(size, provider, method, local, groups):
    """Showcase pattern generator based on mimesis data provider"""

    click.echo("datagenerator(local={}, size={}, provider={}, method={})".format(local, size, provider, method))
    gen = datagenerator(local=local, size=size, provider=provider, method=method)

    for key, values in gen:
        print("\n-- {}".format(key))
        print_columns(values, columns=None, max_rows=4, indent=1)

        with Timer(key=key) as t:
            pm = pattern2(values, max_pattern=groups)
            print( pm.info())


        print(t.printStats(key=key))

    print("Overall timming stats")
    print(t.printStats())


