# -*- coding: utf-8 -*-

"""Console script for dtpattern."""
import sys
import click

from dtpattern.dtpattern import pattern


@click.command()
@click.argument('items', nargs=-1)
@click.option('--size', type=int)

def main(items, size=1):
    """Console script for dtpattern."""
    click.echo("Item list {}".format(items))

    res= pattern(items, size=1)

    click.echo("Result: {}".format(res))




if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
