# -*- coding: utf-8 -*-

"""Console script for dtpattern."""
import sys
import click
from contexttimer import Timer

from dtpattern.dtpattern2 import PatternFinder


@click.group()
def dtpattern2():
    """dtpattern cli , generate patterns for a set of values"""
    pass

@dtpattern2.command()
@click.argument('s1', nargs=1)
@click.argument('s2', nargs=1)
@click.option('--m', type=int, default=5)
@click.option('--mm', type=int, default=-4)
@click.option('--go', type=int, default=-15)
@click.option('--ge', type=int, default=-1)
@click.option('-v', '--verbose', count=True)

def alignpair(s1, s2, verbose,  m, mm, go, ge):
    click.echo("INPUT s1: {}".format(s1))
    click.echo("INPUT s2: {}".format(s2))
    s1,s2 = [ c for c in s1], [ c for c in s2]

    from dtpattern.alignment import alignment_list as al
    aligns=al.align_global(s1,s2, m, mm, go, ge)
    click.echo("Found {} alignment(s)".format(len(aligns)))
    for a in aligns:
        identity, score, align1, symbol, align2 = al.finalize(*a)
        click.echo(al.format_alignment2(identity, score, align1, symbol, align2, indent=2))


@dtpattern2.command()
@click.argument('items', nargs=-1)
@click.option('--size', type=int, default=1)
def items(items,size):

    pm = PatternFinder(max_pattern=size)
    with Timer(factor=1000) as t:
        for value in items:
            pm.add(value)
    click.echo("{} ms".format(t.elapsed))
    click.echo(repr(pm))
