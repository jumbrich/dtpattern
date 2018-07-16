import itertools

from dtpattern.unicode_translate.uc_models import RESULT_PATTERN, FIX_COMB_SYM, VAR_COMB_SYM, PATTERN, FIX_SYMB, \
    VAR_SYMB, UC_SYMBOLS, OPT_PATTERN
from dtpattern.unicode_translate.unicode_categories import _all, CAT, aggregate_CAT, A, aggregate_table, WORD, Lu, Ll

mapping =_all
def make_trans_table(mapping = _all, map_values=CAT):
    translate_table = {}
    rev_trans_table={}
    for o in mapping:
        cset = map_values[o.name]
        for char in cset:
            translate_table[char] = o.value
    return translate_table

#that is level two
string_to_uc_level2 = make_trans_table()
#print("l2",len(trans_table.keys()), len(set(trans_table.values())))
#one higher level

l1_CAT=aggregate_CAT(CAT, A.get_categories_in_level(level=1))
l1_mapping=A.get_categories_in_level(level=1)
string_to_uc_level1 = make_trans_table(mapping=l1_mapping, map_values=l1_CAT)
#print("l1",len(l1_trans_table.keys()), len(set(l1_trans_table.values())))

l0_CAT=aggregate_CAT(CAT, A.get_categories_in_level(level=0))
l0_mapping=A.get_categories_in_level(level=0)
string_to_uc_level0 = make_trans_table(mapping=l0_mapping, map_values=l0_CAT)
#print("l1",len(l0_trans_table.keys()), len(set(l0_trans_table.values())))

all_uc_to_ucname = {a.value: a.name for a in A.get_categories()}
all_uc_to_ucname[WORD.value]= WORD.name

## int to int mappings for aggreate levels

uc_to_uc1 = aggregate_table(A.get_categories_in_level(level=1))
uc_to_uc0 = aggregate_table(A.get_categories_in_level(level=0))
#print (uc_to_uc1, len(uc_to_uc1), len(set(uc_to_uc1.values())))
#print (uc_to_uc0, len(uc_to_uc0), len(set(uc_to_uc0.values())))

def translate_char(char, trans_table=string_to_uc_level2):
    return trans_table.get(char,-1)

def translate(value, trans_table=string_to_uc_level2):
    return [ translate_char(c, trans_table=trans_table) for c in value ]

def translate_all(values, trans_table=string_to_uc_level2, trans_func=translate):
    return [ trans_func(value, trans_table=trans_table) for value in values ]

def unique_order(seq):
    return [[x[0] for x in itertools.groupby(seq)]]


def uniq_uc(values,  trans_table=string_to_uc_level2, trans_func=translate):
    res=set([])
    for value in values:
        ucs = set(trans_func(value, trans_table=trans_table))
        res.update(ucs)
    res= sorted(list(set(res)))
    return ",".join([all_uc_to_ucname[uc] for uc in res])

def higher_level(pattern):
    """
    :param pattern: further aggregate/combine subpatterns for easier readability
    :return:
    """
    _pattern=None
    if isinstance(pattern, RESULT_PATTERN):# or isinstance(pattern, OPT_PATTERN):
        _pattern = pattern.pattern
    if isinstance(pattern, OPT_PATTERN):# or isinstance(pattern, OPT_PATTERN):
        _pattern = pattern.patterns
    if _pattern and not isinstance(_pattern, list):
        return pattern
    else:
        _pat_list=[]
        wordstart=False

        for pat in _pattern:

            if isinstance(pat, OPT_PATTERN):
                _pat_list.append(OPT_PATTERN(higher_level(pat), count=pat.count))
                wordstart = False
            elif isinstance(pat, UC_SYMBOLS):
                _pat_list.append(pat)
                wordstart = False
            else:
                l=1
                if isinstance(pat, VAR_SYMB):
                    l= pat.max_len
                elif isinstance(pat, FIX_SYMB):
                    l = pat.len
                if pat.symbol == Lu.value and l==1:  # Lu
                    _pat_list.append(pat)
                    wordstart = True
                elif pat.symbol == Ll.value:
                    if wordstart:
                        _pat_list.pop() #remove previous 112 pattern
                        if isinstance(pat, FIX_SYMB):
                            _pat_list.append(FIX_COMB_SYM( WORD.value, 1 + pat.len))
                        elif isinstance(pat, VAR_SYMB):
                            _pat_list.append(VAR_COMB_SYM( WORD.value, 1 + pat.fixed, 1 + pat.var, 1 + pat.max_len))
                    else:
                        _pat_list.append(pat)
                else:
                    wordstart=False
                    _pat_list.append(pat)
            prev = pat

    return PATTERN(_pat_list, pattern.count)


def pattern_comparator_length(l2pat1, l2pat2):
    '''
    :param pattern1:
    :param pattern2:
    :return: numbers before ascii
    '''
    pattern1 = l2pat1.uniqorder
    pattern2= l2pat2.uniqorder
    d = len(pattern1) - len(pattern2)
    if d != 0:
        return d
    if pattern1 == pattern2:
        sim = 0
    else:
        p1u = unique_order(pattern1)
        p2u = unique_order(pattern2)
        if p1u > p2u:
            sim = 1
        elif p1u == p2u:
            if pattern1 > pattern2:
                sim = 1
            else:
                sim = -1
        else:
            sim = -1
    # print pattern1, pattern2,sim
    return sim


