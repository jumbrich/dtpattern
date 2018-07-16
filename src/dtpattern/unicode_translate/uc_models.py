import collections
from collections import __init__

#PATTERN = collections.namedtuple("PAT", ['pattern', 'count'])
#L1_PATTERN = collections.namedtuple("L1_PAT", ['pattern', 'count'])
#L2_PATTERN = collections.namedtuple("L2_PAT", ['uniqorder', 'len_l1pats','l1_patterns','count'])
#COM_SEQ = collections.namedtuple("COM_SEQ", ['pattern', 'l2s'])

#FIX_SYMB = collections.namedtuple("FIX_SYMB", ['symbol', 'len'])
#VAR_SYMB = collections.namedtuple("VAR_SYMB", ['symbol', 'fixed', 'var','max_len'])
#OPT_SYMB = collections.namedtuple("OPT_SYMB", ['symbol', 'len'])
#SYMB_GROUP = collections.namedtuple("SYMB_GROUP", ['symbols', 'len'])

#OPT_PATTERN = collections.namedtuple('OPT_PATTERN', ['pattern','count'])
#UC_SYMBOLS = collections.namedtuple('UC_SYMBOLS', ['symbols', 'fixed', 'var', 'max_len'])
FIX_COMB_SYM = collections.namedtuple("FIX_COMB_SYM", ['symbol', 'len'])
VAR_COMB_SYM = collections.namedtuple("VAR_COMB_SYM",  ['symbol', 'fixed', 'var','max_len'])
RESULT_PATTERN  = collections.namedtuple("RESULT_PATTERN", ['pattern', 'count'])

PATTERN  = collections.namedtuple("PAT", ['pattern', 'count'])  # either input value or translated values
PAT_LIST = collections.namedtuple("PAT_LIST", ['patterns', 'count']) # just a list of pattern
UNIQORDER_PATTERN  = collections.namedtuple("UNIQ_ORD_PAT", ['uniqorder', 'patterns', 'count'])
UNIQORDER_PATTERN_GROUP = collections.namedtuple("UNIQ_ORD_PAT_GRP", ['patterns', 'count'])
COM_SEQ = collections.namedtuple("COM_SEQ", ['pattern', 'l2_pattern_group'])
FIX_SYMB = collections.namedtuple("FIX_SYMB", ['symbol', 'len'])
VAR_SYMB = collections.namedtuple("VAR_SYMB", ['symbol', 'fixed', 'var','max_len'])
UC_SYMBOLS = collections.namedtuple('UC_SYMBOLS', ['symbols', 'fixed', 'var', 'max_len'])
OPT_PATTERN = collections.namedtuple('OPT_PATTERN', ['patterns','count'])
