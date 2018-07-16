# -*- coding: utf-8 -*-

"""Console script for dtpattern."""

import click
from csvmimesis.mimesis_data_providers import list_locals, list_providers_methods
from csvmimesis.table_generator import create_data_provider_list
from dtpattern import value_pattern_detection
from dtpattern.unicode_translate.pattern_detection_print import pattern_to_string
from dtpattern.unicode_translate.translate import higher_level

from dtpattern.value_pattern_detection import pattern, uc_agg, pf
from pyjuhelpers.string_format import print_columns
from pyjuhelpers.timer import Timer


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


@click.group()
def demo():
    """demo modus, showcase values and their patterns"""
    pass

@demo.command()

@click.option('-s', '--size', type=int, default=10)
@click.option('-p', '--provider', type=str, default=None)
@click.option('-m', '--method', type=str, default=None)
@click.option('-l', '--local', type=str, default="en")

def demo(size, provider, method, local):
    """Showcase pattern generator based on mimesis data provider"""

    click.echo("datagenerator(local={}, size={}, provider={}, method={})".format(local, size, provider, method))
    gen = datagenerator(local=local, size=size, provider=provider, method=method)

    for key, values in gen:
        print("\n-- {}".format(key))
        print_columns(values, columns=None, max_rows=4, indent=1)

        with Timer(key=key) as t:
            pat = value_pattern_detection.pattern(values, pf=pf)


        print(" ",pat)
        print("  CALL: pattern_to_string(pat, collapse_level=0)")
        pat_str = pattern_to_string(pat, collapse_level=0)
        print("   >> {}".format(pat_str))

        print("  CALL: pattern_to_string(pat, collapse_level=1)")
        pat_str = pattern_to_string(pat, collapse_level=1)
        print("   >> {}".format(pat_str))

        print("  CALL: pattern_to_string(pat, collapse_level=2)")
        pat_str = pattern_to_string(pat, collapse_level=2)
        print("   >> {}".format(pat_str))

        print("  CALL: pattern_to_string( higher_level(pat), collapse_level=2)")
        hl = higher_level(pat)
        print("    ", hl)
        hl_str = pattern_to_string(hl, collapse_level=2)
        print("   >> {}".format(hl_str))

        print(t.printStats(key=key))

    print("Overall timming stats")
    print(t.printStats())
