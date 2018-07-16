import collections
import itertools

from csvmimesis.mimesis_data_providers import list_providers_methods, list_locals
from csvmimesis.table_generator import create_data_provider_list
from dtpattern.pattern_detection import aggregate_based_on_uniqueorder

from dtpattern.suffix_tree_lists import STree
from dtpattern.unicode_translate.uc_models import PATTERN
from dtpattern import pattern_detection, dtpattern2
from dtpattern.unicode_translate.pattern_detection_print import pattern_to_string
from dtpattern.unicode_translate.translate import translate_all, string_to_uc_level2, translate, higher_level, unique_order
import logging

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
                    data = [str(d) for d in data]

                    yield key,data
                except Exception as e:
                    print("Someing wrrong",e)






def pattern1(values):




    v_group = l1(values)
    v_grouped_agg = l2(v_group)
    pre, match, post = l3_shared_groups(v_grouped_agg)


    def get_values(l2_pat_grp:L2_PATTERN_GROUP):
        v = []
        for l2_pat in l2_pat_grp.pattern:
            for l1_pat in l2_pat.l1_pattern:
                for i in range(l1_pat.count):
                    v += ["".join(l1_pat.pattern)]
        return v
    pre_values = get_values(pre)
    patterns = translate_all(pre_values, trans_table=string_to_uc_level2, trans_func=translate)
    _v_group = l1(patterns)
    _v_grouped_agg = l2(_v_group)
    _pre, _match, _post = l3_shared_groups(_v_grouped_agg)

    print(pre)
    print(match)
    print(post)
    if pre.count==len(values):
        _pre, _match, _post = l3_shared_groups(pre)




s="business.company"
#s="business.copyright"
#s="cryptographic.uuid"
s="person.email"
sp = s.split(".") if isinstance(s,str) and len(s)>1 else None
provider= sp[0] if sp and len(sp)>0 else None
method= sp[1] if sp and len(sp)==2 else None


size=10
gen = datagenerator(local='en', size=size, provider=provider, method=method)

#gen= [('test',['123','456','a56','aaa'])]

max_pattern=2
#provider, method=None, None

for key, values in gen:
    print("\n-- {}".format(key))
    print(" V: {}".format(values[:10]))

    #patterns = translate_all(values, trans_table=trans_table, trans_func=translate)
    #print(" P: {}".format(patterns[:10]))

    # L1 = l1_aggregate(patterns)
    # print(" L1: {}".format(L1))
    #
    # L2 = l2_aggregate(grouped=L1)
    # print(" L2: {}".format(L2))


    #patter2(values,max_pattern=max_pattern)

    pattern1(values)

print(Timer.printStats())
