import timeit

from dtpattern.unicode_translate.unicode_categories import *

mapping=[Ll,Nd]

def make_trans_table(mapping):
    translate_table = {}
    for o in mapping:
        cset = CAT[o.name]
        for char in cset:
            translate_table[char] = o.value
    return translate_table

def make_trans_table1(mapping):
    translate_table = {}
    for o in mapping:
        cset = CAT[o.name]
        for char in cset:
            translate_table[ord(char)] = str(o.value)
    return translate_table


trans_table_ord= make_trans_table1(mapping)
trans_table= make_trans_table(mapping)




def translate(value, trans_table=trans_table):
    r=[]
    for c in value:
        r.append(trans_table.get(c,-1))
    return r

def translate_ord(value, trans_table=trans_table_ord):
    r=[]
    for c in value:
        r.append(trans_table.get(ord(c),-1))
    return r

def translate1(value, trans_table=trans_table):
    return [trans_table.get(c,-1) for c in value]
def translate1_ord(value, trans_table=trans_table_ord):
    return [trans_table.get(ord(c),-1) for c in value]

def translate2(value, trans_table=trans_table):
    return [*map(lambda x:trans_table.get(x, -1), value)]
def translate2_ord(value, trans_table=trans_table_ord):
    return list(map(lambda x:trans_table.get(ord(x), -1), value))


def translate3(value, trans_table=trans_table_ord):
    line = value.translate(trans_table)
    return [ line[i:i+2] for i in range(0, len(line), 2)]


def translate4(value, trans_table=trans_table_ord):
    line= value.translate(trans_table)
    import re
    return re.findall('..',line)


def translate_all(values, translate=None, trans_table=None):
    return [translate(value,trans_table=trans_table) for value in values]



value=""

values=[value,value,value]

s_import= 'from __main__ import translate,translate_ord,translate1,translate1_ord,' \
          'translate2,translate2_ord, value, trans_table, trans_table_ord, translate3, translate4,translate_all,values'
runs=3000
print(translate_all(values, translate=translate1, trans_table=trans_table))

t_func=[
    ("translate(value, trans_table=trans_table)",translate(value, trans_table=trans_table)),
    ("translate_ord(value, trans_table=trans_table_ord)",translate_ord(value, trans_table=trans_table_ord)),
    ("translate1(value, trans_table=trans_table)",translate1(value, trans_table=trans_table)),
    ("translate1_ord(value, trans_table=trans_table_ord)",translate1_ord(value, trans_table=trans_table_ord)),
    ("translate2(value, trans_table=trans_table)",translate2(value, trans_table=trans_table)),
    ("translate2_ord(value, trans_table=trans_table_ord)",translate2_ord(value, trans_table=trans_table_ord)),
    ("translate3(value, trans_table=trans_table_ord)",translate3(value, trans_table=trans_table_ord)),
    ("translate4(value, trans_table=trans_table_ord)",translate4(value, trans_table=trans_table_ord)),

    ("translate_all(values, translate=translate1, trans_table=trans_table)",translate_all(values, translate=translate1, trans_table=trans_table)),
]

for f in t_func:
    duration = timeit.timeit( f[0], s_import, number=runs)*1000
    print("{:>14} msec {:.5f}  {}".format( duration, duration/runs,f[0]))
    print("  out:{}".format(f[1]))

