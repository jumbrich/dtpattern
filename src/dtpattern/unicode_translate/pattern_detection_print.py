
from dtpattern.unicode_translate.translate import all_uc_to_ucname
from dtpattern.unicode_translate.uc_models import FIX_COMB_SYM, VAR_COMB_SYM, FIX_SYMB, VAR_SYMB, UC_SYMBOLS, \
    OPT_PATTERN
from multipledispatch import dispatch

import structlog
log = structlog.get_logger()
def subpattern_to_string(pattern, rev_trans_table=all_uc_to_ucname, intend=1):
    s=""
    if not isinstance(pattern, list):
        s = "{}".format(pattern)
        pattern = pattern.pattern

    _pattern=iter(pattern)
    while True:
        try:
            pat= next(_pattern)

            if isinstance(pat, int):
                s += "\n{}-{:^4} {}".format(" "*intend*2,rev_trans_table[pat],pat)
            elif isinstance(pat, FIX_SYMB):
                s+= "\n{}-{:^4} {}".format(" "*intend*2,rev_trans_table[pat.symbol],pat)
            elif isinstance(pat, VAR_SYMB):
                s += "\n{}-{:^4} {}".format(" "*intend*2,rev_trans_table[pat.symbol],pat)
            elif isinstance(pat, OPT_PATTERN):
                s += "\n{}-{}".format(" "*intend*2,pat)
                s+=subpattern_to_string(pat.pattern,rev_trans_table=rev_trans_table,intend=intend+1)
        except Exception as e:
            break
    return s

def pattern_to_string(pattern, rev_trans_table=all_uc_to_ucname, collapse_level=0,with_gap=True):

    f = pattern_to_string_dispatch(rev_trans_table=rev_trans_table, collapse_level=collapse_level, with_gap=with_gap).to_string

    if not isinstance(pattern, list):
        pattern = pattern.pattern
    if not isinstance(pattern, list):
       return f(pattern)

    s=""
    _pattern=iter(pattern)
    _prev = None
    _prev_cnt = 0

    while True:
        try:
            pat= next(_pattern)
            if isinstance(pat, FIX_SYMB):
                if _prev is not None and _prev != pat.symbol:
                    s += f(FIX_SYMB(_prev, _prev_cnt))
                    _prev_cnt = 0
                _prev_cnt += pat.len
                _prev = pat.symbol
            else:
                if _prev is not None:
                    s += f(FIX_SYMB(_prev, _prev_cnt))
                    _prev_cnt = 0
                _prev = None

                s += f(pat)
        except StopIteration:
            break
        except Exception as e:
            log.exception("During pattern_to_string",pat=pat)
            raise e
    if _prev:
        s += f(FIX_SYMB(_prev, _prev_cnt))

    return s.strip()


class pattern_to_string_dispatch(object):

    def __init__(self, rev_trans_table=all_uc_to_ucname, collapse_level=0, with_gap=True):
        """Initialize the class."""
        self.rev_trans_table = rev_trans_table
        self.collapse_level = collapse_level
        self.fixed="*"
        self.optional="?"
        self.with_gap=with_gap

    @dispatch(int)
    def to_string(self, pattern):
        return "{}".format(self.rev_trans_table[pattern])

    @dispatch(str)
    def to_string(self, pattern):
        return "'{}'".format(pattern)

    def format(self, value:str):
        if self.with_gap:
            return "{} ".format(value)
        return value

    @dispatch(str, int)
    def to_string(self, symbol_str, len):
        if len == 1:
            s = "{}".format(symbol_str)
        elif self.collapse_level == 0:
            s = "{}".format(symbol_str * len)
        elif self.collapse_level == 1:
            s = "{}{}".format(symbol_str, self.fixed * (len - 1))
        else:
            s = "{}{}".format(symbol_str, len)
        return self.format(s)

    @dispatch(int,int)
    def to_string(self, symbol, len):
        return self.to_string(self.to_string(symbol), len)

    @dispatch(int, int, int, int)
    def to_string(self, symbol, fixed, var, max_len):
        return self.to_string(self.to_string(symbol), fixed, var, max_len)

    @dispatch(str, int, int, int)
    def to_string(self, symbol_str, fixed, var, max_len):
        if self.collapse_level < 2:
            s = "{0}{1}{2}".format(symbol_str, self.fixed * (fixed - 1), self.optional * var)
        else:
            s = "{0}{{{1},{2}}}".format(symbol_str, fixed, max_len)
        return self.format(s)

    @dispatch(FIX_SYMB)
    def to_string(self, pattern):
        s= pattern.symbol
        if isinstance(s,str):
            s="'{}'".format(s)
        return self.to_string(s,pattern.len)

    @dispatch(FIX_COMB_SYM)
    def to_string(self, pattern):
        return self.to_string(pattern.symbol, pattern.len)

    @dispatch(VAR_SYMB)
    def to_string(self, pat):
        s = pat.symbol
        if isinstance(s, str):
            s = "'{}'".format(s)
        return self.to_string(s, pat.fixed, pat.var, pat.max_len)


    @dispatch(VAR_COMB_SYM)
    def to_string(self, pat):
        return self.to_string(pat.symbol, pat.fixed, pat.var, pat.max_len)


    @dispatch(UC_SYMBOLS)
    def to_string(self, pat):
        s="[{0}]".format(",".join([self.to_string(s)for s in pat.symbols]))
        return self.to_string(s, pat.fixed, pat.var, pat.max_len)

    @dispatch(OPT_PATTERN)
    def to_string(self, pat):
        pat_str = pattern_to_string(pat.patterns, rev_trans_table=all_uc_to_ucname, collapse_level=self.collapse_level)

        s="({})#{}".format(pat_str,pat.count)
        return self.format(s)

    # @dispatch(OPT_SYMB)
    # def to_string(self, pat):
    #     pat_str = self.to_string(pat.symbol)
    #     if pat.len == 1:
    #         return "({}) ".format(pat_str)
    #     elif self.collapse_multi:
    #         return "({}){} ".format(pat_str, pat.len)
    #     else:
    #         return "({}){} ".format(pat_str, self.fixed * (pat.len - 1))
    #
    # @dispatch(SYMB_GROUP)
    # def to_string(self, pat):
    #     pat_str=",".join([self.to_string(sym)  for sym in pat.symbols])
    #     if pat.len == 1:
    #         return "[{}] ".format(pat_str)
    #     elif self.collapse_multi:
    #         return "[{}]{} ".format(pat_str, pat.len)
    #     else:
    #         return "[{}]{} ".format(pat_str, self.fixed * (pat.len - 1))

