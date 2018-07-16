import itertools
from difflib import SequenceMatcher as SM



from dtpattern.suffix_tree_lists import STree
from dtpattern.unicode_translate.translate import translate_all, string_to_uc_level2, translate, unique_order, \
    string_to_uc_level0, \
    string_to_uc_level1, uc_to_uc0, uc_to_uc1
from dtpattern.unicode_translate.uc_models import RESULT_PATTERN, PATTERN, PAT_LIST, UNIQORDER_PATTERN, \
    UNIQORDER_PATTERN_GROUP, FIX_SYMB, VAR_SYMB, UC_SYMBOLS, OPT_PATTERN
from pyjuhelpers.timer import timer


class PatternFinder(object):

    def __init__(self, name, aggregator=None, level=3):
        self.aggegator = aggregator
        self.level=level
        self.name = name

    def translate(self, values):
        return [[c for c in v] for v in values]

    # def parse_pat_list(self, pat,_l):
    #     for p in pat.patterns:
    #         if isinstance(p, UNIQORDER_PATTERN_GROUP):
    #             if self.aggegator:
    #                 pat_values = get_values(p)
    #                 _pat = self.aggegator.pattern(pat_values)
    #                 if len(_pat.pattern) != 1 or not isinstance(_pat.pattern[0], UC_SYMBOLS):
    #                     _l+=_pat.pattern
    #                     break
    #             unique_ucs = list(sorted(set([y for x in p.patterns for y in x.uniqorder])))
    #             l = [len(y.pattern) for x in p.patterns for y in x.patterns]
    #             _l.append(UC_SYMBOLS(unique_ucs, min(l), max(l) - min(l), max(l)))
    #         elif isinstance(p, PAT_LIST):
    #             __l = []
    #             self.parse_pat_list(p,__l)
    #             if p.count < pat.count:
    #                 _l.append(OPT_PATTERN(__l, p.count))
    #             else:
    #                 _l += __l
    #         else:
    #             _l.append(p)

    def parse_pat_list(self, pat,_l):
        for p in pat.patterns:
            if isinstance(p, PAT_LIST):
                __l = []
                self.parse_pat_list(p,__l)
                if p.count < pat.count:
                    _l.append(OPT_PATTERN(__l, p.count))
                else:
                    _l += __l
            else:
                _l.append(p)

    def parse_uopg(self, pat, _l):
        if self.aggegator:
            pat_values = get_values(pat)
            _pat = self.aggegator.pattern(pat_values)
            return _pat
        else:
            unique_ucs = list(sorted(set([y for x in pat.patterns for y in x.uniqorder])))
            l = [len(y.pattern) for x in pat.patterns for y in x.patterns]
            return UC_SYMBOLS(unique_ucs, min(l), max(l) - min(l), max(l))

    def ucaggregate_pat_list(self, pat_list, _l):
        for pat in pat_list:
            if isinstance(pat, UNIQORDER_PATTERN_GROUP):
                _pat = self.parse_uopg(pat, _l)
                if isinstance(_pat, UC_SYMBOLS):
                    _l.append(_pat)
                else:
                    _l += _pat.pattern
            elif isinstance(pat, OPT_PATTERN):
                _sl = []
                self.ucaggregate_pat_list(pat.patterns,_sl)
                _l.append(OPT_PATTERN(_sl, pat.count))
            else:
                _l.append(pat)

    def score(self, pat_list, cnt):
        _score=0
        fix=1
        var=1

        uni=1
        ucs=1
        l=len(pat_list)
        for i, pat in enumerate(pat_list):
            if isinstance(pat, FIX_SYMB):

                _score+=fix
            elif isinstance(pat, VAR_SYMB):
                _score += var
            elif isinstance(pat, OPT_PATTERN):
                #print(">-")
                s= self.score(pat.patterns, pat.count)
                sc = s * (pat.count / cnt) if cnt >0 else s
                #print(s," weight",pat.count, cnt)
                #print("<-")
                _score += sc
            elif isinstance(pat, UNIQORDER_PATTERN_GROUP):
                _score += uni
                uni -= 1
            elif isinstance(pat, UC_SYMBOLS):
                _score += ucs
                ucs -= 1
            else:
                print("Hllo", pat)
            #print(i, _score, pat)
        #print(_score,l)

        return _score/l if l >0 else 0


    def pattern(self, values:[])-> RESULT_PATTERN:

        values = self.translate(values)

        uni_pats = to_unique_patterns(values)
        g_up = group_by_unique_order(uni_pats)

        res = find_shared_patterns(g_up, level=self.level)

        #flatten patterns
        pat_list = []
        for pat in res.patterns:
            _l = []
            if isinstance(pat, PAT_LIST):
                self.parse_pat_list(pat,_l)
            else:
                raise Exception("HELLO")
            if pat.count < g_up.count:
                pat_list.append(OPT_PATTERN(_l, pat.count))
            else:
                pat_list += _l

        score = {}
        _sc1 = self.score(pat_list, len(values))
        score[self.name] = {'score' :_sc1, 'pat':pat_list}
        #print("SCORE [{}] #{}: {} ".format(self.name, len(pat_list), _sc1))
        #for val in pat_list:
        #    print(" {}".format(val))

        if self.aggegator:
            _pat = self.aggegator.pattern(values)
            _sc2 = self.score(_pat.pattern, pat.count)
            #print("SCORE [{}] #{}: {} ".format(self.aggegator.name, len(_pat.pattern), _sc2))
            #for val in _pat.pattern:
            #    print(" {}".format(val))
            score[self.aggegator.name] = {'score' :_sc2, 'pat':_pat.pattern}

            if _sc2 > _sc1:
                pat_list = _pat.pattern

        _l=[]
        self.ucaggregate_pat_list(pat_list, _l)




        #_sc3 = self.score(_l)
        #score[self.name+"uc"] = {'score': _sc3, 'pat': _l}

        res = RESULT_PATTERN(_l, len(values))

        return res
        # _l=[]
        # for pat in pat_list:
        #     if isinstance(pat, UNIQORDER_PATTERN_GROUP):
        #         if self.aggegator:
        #             pat_values = get_values(pat)
        #             _pat = self.aggegator.pattern(pat_values)
        #             _l+=_pat.pattern
        #         else:
        #             unique_ucs = list(sorted(set([y for x in pat.patterns for y in x.uniqorder])))
        #             l = [len(y.pattern) for x in pat.patterns for y in x.patterns]
        #             _l.append(UC_SYMBOLS(unique_ucs, min(l), max(l) - min(l), max(l)))
        #     else:
        #         _l.append(pat)
        #
        # return RESULT_PATTERN(_l, len(values))


class UnicodeCategoryAggregator(PatternFinder):

    def __init__(self, name, aggregator=None, level=1, trans_table=string_to_uc_level2, trans_func=translate):
        super(UnicodeCategoryAggregator, self).__init__(name, aggregator=aggregator, level=level)
        self.translate_all = lambda x:  translate_all(x, trans_table=trans_table, trans_func=trans_func)

    def translate(self, values):
        return self.translate_all(values)

    def __repr__(self):
        return "{}".format(self.name)
    def __str__(self):
        return self.__repr__()
def get_values(l2_pat_grp: UNIQORDER_PATTERN_GROUP):
    v = []
    for l2_pat in l2_pat_grp.patterns:
        for l1_pat in l2_pat.patterns:
            for i in range(l1_pat.count):
                v += [l1_pat.pattern]
    return v

uc_l0 = UnicodeCategoryAggregator( "l0",trans_table=uc_to_uc0, trans_func=translate)
uc_l1 = UnicodeCategoryAggregator( "l1",trans_table=uc_to_uc1, trans_func=translate, aggregator=uc_l0)
uc_agg = UnicodeCategoryAggregator( "l2", trans_table=string_to_uc_level2, trans_func=translate, aggregator=uc_l1)
pf = PatternFinder("raw",aggregator=uc_agg)


@timer(key="pattern")
def pattern(values:list, pf=pf)-> RESULT_PATTERN:

    return pf.pattern(values)


def to_unique_patterns(values:list) -> PAT_LIST:
    """
    group values list by their values and convert them into PATTERN
    :param values: list of input values
    :return: PAT_LIST
    """
    values.sort(key=len)
    group = [PATTERN(k, sum(1 for i in g)) for k, g in itertools.groupby(values)]
    return PAT_LIST(group, sum(map(lambda x: x.count, group)))

def group_by_unique_order(pat_list: PAT_LIST) -> UNIQORDER_PATTERN_GROUP:
    """
    Groups a list of PATTERN based on their unique order of values
    :param l1_group:
    :return:
    """
    v_grouped_agg = []
    for uniorder, g in itertools.groupby(pat_list.patterns, lambda x: unique_order(x.pattern)):
        l1pats = [l1pat for l1pat in g]  #exhaust groupby iterator
        if isinstance(uniorder, list):
            uniorder=uniorder[0]
        v_grouped_agg.append(UNIQORDER_PATTERN(uniorder, l1pats, sum(map(lambda x: x.count, l1pats))))

    return UNIQORDER_PATTERN_GROUP(v_grouped_agg, sum(map(lambda x: x.count, v_grouped_agg)))


def find_shared_patterns(uniq_pat_group: UNIQORDER_PATTERN_GROUP, level=1)-> PAT_LIST:
    if len(uniq_pat_group.patterns) == 0:
        return None
    if len(uniq_pat_group.patterns) == 1:
        #one group with the same unique order of pattern symbols
        uniqorder_pattern = uniq_pat_group.patterns[0]
        pat =  aggregate_uniqorder_pattern(uniqorder_pattern) #PAT_LIST
        return PAT_LIST([pat], uniq_pat_group.count)

    #first, find the longest common sequenece
    uniqorder_keys = [l2pat.uniqorder for l2pat in uniq_pat_group.patterns]
    st = STree(uniqorder_keys)
    com_seq_pattern = st.lcs()

    #total_count = sum(map(lambda x: x.count, uniq_pat_group.patterns)) if not total_count else total_count
    if com_seq_pattern is None or len(com_seq_pattern)==0:
        # no common subsequence
        # this is tricky, because we need ot find a way to return all
        return PAT_LIST([PAT_LIST([uniq_pat_group], uniq_pat_group.count)], uniq_pat_group.count)
    else:
        pre, match, post = split_group(uniq_pat_group, com_seq_pattern)
        if len(com_seq_pattern)<level and pre.count != 0 and post.count!=0:
            return PAT_LIST([PAT_LIST([uniq_pat_group], uniq_pat_group.count)], uniq_pat_group.count)

        if all([isinstance(c,str) for c in com_seq_pattern]):
            #we have a raw character match, lets check if there are var symbols in it-This can cause serious problems later on
            #e.g. test datetime.data
            for __pat in match.patterns:
                if isinstance( __pat, VAR_SYMB):
                    return PAT_LIST([PAT_LIST([uniq_pat_group], uniq_pat_group.count)], uniq_pat_group.count)



        pat_list=[]
        if pre.count>0:
            pre_pat = find_shared_patterns(pre, level=level)

            pat_list.append(pre_pat)
        pat_list.append(match)
        if post.count > 0:
            post_pat = find_shared_patterns(post, level=level)
            pat_list.append(post_pat)

        return PAT_LIST(pat_list, uniq_pat_group.count)


def split_group(uniq_pat_group: UNIQORDER_PATTERN_GROUP, com_seq_pattern:[])-> (
UNIQORDER_PATTERN_GROUP, RESULT_PATTERN, UNIQORDER_PATTERN_GROUP):
    pre_patterns_dict = {}
    post_patterns_dict = {}
    matched_patterns_list = []

    cnt = 0
    for uniqorder_pattern in uniq_pat_group.patterns:
        match = SM(None, list(com_seq_pattern), uniqorder_pattern.uniqorder, autojunk=False)\
            .find_longest_match(0, len(com_seq_pattern), 0, len(uniqorder_pattern.uniqorder))

        if match.size != len(com_seq_pattern):
            raise Exception("This l2 pattern has no common sequence pattern ")
        if match.size != 0:
            pre, post = uniqorder_pattern.uniqorder[:match.b], uniqorder_pattern.uniqorder[match.b + match.size:]

            l2_pres, l2_matched, l2_posts = [], [], []
            pre_cnt, match_cnt, post_cnt = 0, 0, 0

            for pat in uniqorder_pattern.patterns:
                _pres, _matched, _posts = [], [], []

                grouped = itertools.groupby(pat.pattern)
                # iterate over the orig patterns for this l2pattern
                if len(pre) > 0:
                    pre_cnt += pat.count
                    for s in pre:
                        k, g = next(grouped)
                        if s != k:
                            print('autsch')
                        else:
                            _pres += [k for k in g]
                    l2_pres.append(PATTERN(_pres, pat.count))

                for s in com_seq_pattern:
                    match_cnt += pat.count
                    cnt += pat.count
                    k, g = next(grouped)
                    if s != k:
                        print('autsch')
                    else:
                        _matched += [k for k in g]
                l2_matched.append(PATTERN(_matched, pat.count))

                if len(post) > 0:
                    post_cnt += pat.count
                    for s in post:
                        k, g = next(grouped)
                        if s != k:
                            print('autsch')
                        else:
                            _posts += [k for k in g]
                    l2_posts.append(PATTERN(_posts, pat.count))

            if len(pre) > 0:
                pre_patterns_dict.setdefault(tuple(pre),[]).append( (l2_pres,pre_cnt) )
            if len(post) > 0:
                post_patterns_dict.setdefault(tuple(post), []).append((l2_posts, post_cnt))
            matched_patterns_list+=l2_matched


    matched_pattern = aggregate_based_on_uniqueorder(
        UNIQORDER_PATTERN(com_seq_pattern, matched_patterns_list, cnt))

    pre_list=[]
    for key, values in pre_patterns_dict.items():
        l2_pres=[]
        pre_cnt=0
        for p,cnt in values:
            l2_pres+=p
            pre_cnt+=cnt
        pre_list.append(UNIQORDER_PATTERN(list(key), l2_pres, pre_cnt))

    post_list = []
    for key, values in post_patterns_dict.items():
        l2_pres = []
        pre_cnt = 0
        for p, cnt in values:
            l2_pres += p
            pre_cnt += cnt
        post_list.append(UNIQORDER_PATTERN(list(key), l2_pres, pre_cnt))
    pre_group = UNIQORDER_PATTERN_GROUP(pre_list, sum(map(lambda x: x.count, pre_list)))
    post_group = UNIQORDER_PATTERN_GROUP(post_list, sum(map(lambda x: x.count, post_list)))
    return pre_group, matched_pattern, post_group

def aggregate_uniqorder_pattern(uniqorder_pattern: UNIQORDER_PATTERN) -> PAT_LIST:
    if len( uniqorder_pattern.uniqorder ) == 1:
        # one uniqorder_pattern with only one symbol,
        ''' This assumes that all patterns have the same set of symbols
                returns a single pattern for all input patterns
            '''
        total = sum(map(lambda x: x.count, uniqorder_pattern.patterns))
        var_sym = aggregate_group_of_same_symbol([l1pat.pattern for l1pat in uniqorder_pattern.patterns])
        return PAT_LIST([var_sym], total)

    else:
        #one uniqorder_pattern but with several symbols
        # aggregate each symbol and concat the groups
        return aggregate_based_on_uniqueorder(uniqorder_pattern)

def aggregate_group_of_same_symbol(patterns:[]):

    symbols, p = None, None
    max_len = 0

    for pattern in patterns:
        max_len= max(max_len,len(pattern))

        symbols = set(pattern) if symbols is None else symbols
        if len(symbols)>1:
            raise ValueError("We have more than one symbol: {}".format(symbols))
        if set(pattern) != symbols:
            raise ValueError("Diff symbols in list of patterns: {} vs {}".format(symbols, set(pattern)))

        if p is None:  # nothing aggregated yet
            p = pattern
        else:
            a = p[::-1]
            b = pattern[::-1]
            match = SM(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))

            p = a[match.a:match.a+match.size]
    if len(p) == max_len:
        return FIX_SYMB(symbols.pop(), max_len)
    return VAR_SYMB(symbols.pop(), len(p), max_len - len(p), max_len)


def aggregate_based_on_uniqueorder(uniqorder_pattern: UNIQORDER_PATTERN):
    p_groups = [[] for a in range(0, len(uniqorder_pattern.uniqorder))]
    cnt = 0
    for l1pat in uniqorder_pattern.patterns:
        cnt += l1pat.count
        for i, x in enumerate(itertools.groupby(l1pat.pattern)):
            p_groups[i].append([a for a in x[1]])

    agg_pattern=[]
    for patterns in p_groups:
        _agg_pattern= aggregate_group_of_same_symbol(patterns)
        if isinstance(_agg_pattern, list):
            agg_pattern += _agg_pattern
        else:
            agg_pattern.append(_agg_pattern)

    return PAT_LIST(agg_pattern, cnt)
