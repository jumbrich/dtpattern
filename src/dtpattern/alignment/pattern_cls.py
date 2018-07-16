import functools
import heapq
from operator import itemgetter


from dtpattern.alignment.merge import merge

from dtpattern.alignment.alignment_cls import Alignment
from dtpattern.timer import timer
from dtpattern.unicode_translate.pattern_detection_print import pattern_to_string
from dtpattern.unicode_translate.uc_models import PATTERN, FIX_SYMB, OPT_SYMB

import structlog
log = structlog.get_logger()

@functools.total_ordering
class Pattern(object):

    @timer(key='patinit')
    def __init__(self, value:str, topk=3, translate=None):
        self.symbol = [ c for c in value ]
        self._count = 1
        self.topk=topk
        self._vcounts = [ {c:1} for c in value ]
        self._merge = merge(translate=translate)

    def __eq__(self, other):
        if self._count == other._count:
            if len(self.symbol) == len(other.symbol):
                first_set = set(map(tuple, self.symbol))
                secnd_set = set(map(tuple, other.symbol))
                return first_set == secnd_set
        return False

    def __lt__(self, other):
        if self._count == other._count:
            if len(self.symbol) == len(other.symbol):
                return False
            else:
                return len(self.symbol) < len(other.symbol)
        else:
            return self._count < other._count

    def merge_with_pattern(self, p_beta, alignment):
        """ merge a pattern into this pattern based on the computed alignment
            in principle, this is the same as updating a pattern with an alignment,
            the only difference is the value counts of pattern beta
        """
        best_sym = alignment.best()['symbol']
        self.update_symbol(best_sym, beta_counts=p_beta._vcounts)
        self._count+=p_beta._count-1

    def update_with_alignment(self,alignment):
        if not isinstance(alignment, Alignment):
            raise ValueError("Method accepts only Alignment objects")

        best_sym=alignment.best()['symbol']
        self.update_symbol(best_sym)


    def update_counts(self, pos, value, cnt=None):
        return
        self._vcounts[pos].setdefault(value, 0)
        if cnt:
            self._vcounts[pos][value] += cnt
        else:
            self._vcounts[pos][value] += 1

        if len(self._vcounts[pos])>self.topk:
            d={k:v for k,v in heapq.nlargest(self.topk, self._vcounts[pos].items(), key=itemgetter(1))}
            #print(self._vcounts[pos],d)
            self._vcounts[pos]=d

    @timer(key='update_symbol')
    def update_symbol(self, symbol, beta_counts=None):
        log.debug("[MERGE] Merging alignment {} into {}".format(symbol, self))
        m=[]

        if beta_counts is not None:
            pass

        a_i = 0
        b_i = 0
        for i, s in enumerate(symbol):
            if isinstance(s, str) or isinstance(s, FIX_SYMB):
                #str means a character in both patterns
                m.append(s)
                self.update_counts(i,s) #update new mapping
                a_i += 1
                b_i += 1
            elif isinstance(s, list):
                if len(s)==1:
                    #normally only happens if we compare two patterns with the same symbols
                    m.append(s)
                    #logger.debug("SINGLE VALUE {}".format(s))
                elif len(s)!=2:
                    log.warning(" 0 or more than two elements in alignment list {}". format(s))
                else:
                    """
                    list -> means that we have one of the following cases:
                     1) s[0]:str and s[1]:str
                        => translate both elements and build the set
                    """
                    a1, a2 = s[0], s[1]

                    if '' in s:
                        if a1 == '':
                            # this is an insert, beta has an additional element
                            self._vcounts.insert(i, {None:0})
                            opt = a2
                            if isinstance(opt, str):
                                self.update_counts(i,opt)
                                #opt = utils.translate(opt)
                            if isinstance(opt, OPT_SYMB):
                                opt = opt.symbol
                            m.append(OPT_SYMB(opt,1))
                        else:
                            opt = a1
                            if isinstance(opt, OPT_SYMB):
                                opt = opt.symbol
                            m.append( OPT_SYMB(opt,1))
                            self.update_counts(i, None)
                    else:
                        _m = self._merge(a1,a2)
                        m.append(_m)
            else:
                print("CASE MISSING IN update symbol")
        self.symbol = m
        self._count += 1
        log.debug("[MERGED] Result of Merging alignment is: %s",self)

    @timer(key='_serialse')
    def _serialise(self):
        pat = PATTERN(self.symbol,self._count)

        s= pattern_to_string(pat, collapse_multi=False)

        return s

    @timer(key='_compact')
    def _compact(self):

        it=iter(self.symbol)

        _s=''
        l=next(it, None)
        while l:
            try:
                _s_ = ""
                if isinstance(l,str):
                    _s_ ="'"
                    while True:
                        _s_+=l
                        l=next(it,None)
                        if not isinstance(l,str):
                            break

                    _s_+="'"
                elif isinstance(l,list):
                    _prev = l
                    _c=1
                    while True:
                        l=next(it,None)
                        if not isinstance(l,list):
                            break
                        if l == _prev:
                            _c+=1
                        else:
                            break
                    if len(_prev)==1:
                        if _c>1:
                            _s_ = "{}{}".format(_prev[0],_c)
                        else:
                            _s_ = "{}".format(_prev[0])
                    else:
                        _ps="".join(_prev)
                        _s_="[{}]".format(_ps)

                elif isinstance(l,tuple):
                    _prev = l
                    _c = 1
                    while True:
                        l = next(it,None)
                        if not isinstance(l, tuple):
                            break
                        if l == _prev:
                            _c += 1
                        else:
                            break
                        _prev=l
                    if _c ==1:
                        if isinstance(_prev[0], list):
                            if len(_prev[0])==1:
                                sl = "{0}".format(','.join(map(str, _prev[0])))
                            else:
                                sl = "[{0}]".format(','.join(map(str, _prev[0])))
                        else:
                            sl=_prev[0]
                        _s_ = "{}?".format(sl)
                    else:
                        if isinstance(_prev[0], list):
                            if len(_prev[0])==1:
                                sl = "{0}".format(','.join(map(str, _prev[0])))
                            else:
                                sl = "[{0}]".format(','.join(map(str, _prev[0])))
                        else:
                            sl=_prev[0]
                        _s_ = "{{{},{},{}}}".format(sl,_prev[1],_c)

                _s+=_s_
            except StopIteration:
                break

        return _s

    def __str__(self):
        return "{}(#{}): {}".format('PAT',self._count, self._serialise())#, self._compact())

    def __repr__(self):

        r=[
           ('list', self.symbol),
           ('string', self._serialise()),
           ('compact', self._serialise()),
            ('#freq', self._vcounts)

           ]

        s="\n#**-| {}(#values: {}): {} |-**".format(self.__class__.__name__, self._count, self._serialise())
        for k,v in r:
            s += "\n * {:<8} {}".format(k,v)

        s+="\n *-----"
        return s
