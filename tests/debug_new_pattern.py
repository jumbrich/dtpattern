
from csvmimesis.mimesis_data_providers import list_providers_methods, list_locals
from csvmimesis.table_generator import create_data_provider_list
from dtpattern.unicode_translate.uc_models import PATTERN
from dtpattern import pattern_detection, dtpattern2, value_pattern_detection
from dtpattern.unicode_translate.pattern_detection_print import pattern_to_string
from dtpattern.unicode_translate.translate import translate_all, string_to_uc_level2, translate, higher_level
import logging

from dtpattern.value_pattern_detection import uc_agg
from pyjuhelpers.logging import defaultConf
from pyjuhelpers.timer import Timer

logging.config.dictConfig(defaultConf)

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


def pattern1(key,values):
    with Timer(key=key) as t:
        pat = pattern_detection.pattern(values,max_opt_depth=2)
        if isinstance(pat, PATTERN):
            assert pat.count == size
    print(t.printStats(key=key))


    #print(subpattern_to_string(pat))

    pat_str= pattern_to_string(pat,collapse_multi=False)
    print("PAT>> {} {}".format(pat_str, pat))

    hl= higher_level(pat)
    hl_str=pattern_to_string(hl,collapse_multi=False)
    print("HL>> {} {}".format(hl_str, hl))

    if "Lu Ll" not in pat_str:
       assert pat_str == hl_str

def pattern3(key,values):
    with Timer(key=key) as t:
        pat = value_pattern_detection.pattern(values, pf=uc_agg)
    print(t.printStats(key=key))

    print(pat)
    pat_str = pattern_to_string(pat, collapse_level=0)
    print("PAT>> {} {}".format(pat_str, pat))
    pat_str = pattern_to_string(pat, collapse_level=1, with_gap=False)
    print("PATL1>> {} {}".format(pat_str, pat))
    pat_str = pattern_to_string(pat, collapse_level=2)
    print("PATL2>> {} {}".format(pat_str, pat))

    hl = higher_level(pat)
    hl_str = pattern_to_string(hl, collapse_level=2)
    print("HL>> {} {}".format(hl_str, hl))

    #if "Lu Ll" not in pat_str:
    #    assert pat_str == hl_str
    #print(t.printStats(key=key))

def patter2(values,max_pattern=3):
    pm = dtpattern2.pattern(values,max_pattern=max_pattern)
    print(pm)


s="business.company"
#s="business.copyright"
#s="cryptographic.uuid"
s=None#"address"
#s="text.title"#"text.title"#"numbers.floats"#"business.company"#"internet.top_level_domain"
sp = s.split(".") if isinstance(s,str) and len(s)>1 else None
provider= sp[0] if sp and len(sp)>0 else None
method= sp[1] if sp and len(sp)==2 else None


size=10
gen = datagenerator(local='en', size=size, provider=provider, method=method)

#gen= [('test',['AT-123','AT-456','AT-','AT-'])]


datetime=[
    ('a', ['2022-12-12 13:49:35', '2011-01-04 08:15:39', '2031-02-23 04:03:43', '2023-11-21 01:57:45', '2003-05-27 06:05:34', '2025-02-09 15:02:17', '2000-07-23 23:29:10', '2028-11-01 20:55:58', '2022-01-13 07:19:03', '2033-10-15 12:08:45']),
('a', ['2022-12-12T13:49:35', '2011-01-04T08:15:39', '2031-02-23T04:03:43', '2023-11-21T01:57:45', '2003-05-27T06:05:34']),
('a', ['2022-12-12T13:49:35Z', '2011-01-04T08:15:39Z', '2031-02-23T04:03:43Z', '2023-11-21T01:57:45Z', '2003-05-27T06:05:34Z']),
('a', ['123.2344','23.23','797239479234.72934702734']),
('a', ['0.2344','0.23','0.72934702734']),
('a', ['10.2344','20.23','0.72934702734']),
('a', ['100.2344','1001.23','100.72934702734']),
('a', ['+100.2344','+1001.23','+100.72934702734']),
('a', ['+100.2344','+1001.23','100.72934702734']),
('a', ['+100.2344','1001.23','-100.72934702734']),
('a', ['01.2344','02.2344','03.729347027344']),

('a', ['+10','-20','40']),
('a', ['10','20','40']),('a', ['+10','+20','+40']),
('a', ['-10','-20','-40']),


]
gen=datetime


max_pattern=2
#provider, method=None, None

for key, values in gen:
    print("\n-- {}".format(key))
    print(" V: {}".format(values[:10]))

    patterns = translate_all(values, trans_table=string_to_uc_level2, trans_func=translate)
    print(" P: {}".format(patterns[:10]))

    # L1 = l1_aggregate(patterns)
    # print(" L1: {}".format(L1))
    #
    # L2 = l2_aggregate(grouped=L1)
    # print(" L2: {}".format(L2))


    #patter2(values,max_pattern=max_pattern)

    pattern3(key,values)

print(Timer.printStats())
