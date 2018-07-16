import functools
from enum import Enum

from dtpattern.alignment.alignment_cls import Alignment, compare
from dtpattern.alignment.pattern_cls import Pattern
from dtpattern.unicode_translate.translate import translate_char
from dtpattern.unicode_translate.translate import string_to_uc_level2

from pyjuhelpers.string_format import reindent

import structlog
from pyjuhelpers.timer import timer

log = structlog.get_logger()



class CompressStrategy(Enum):
    ALL_AFTER=1

c_s={
    CompressStrategy.ALL_AFTER: "compress after a new pattern got created, compress all other pattern with 100% identity",

}

def compress_strategies():
    s=""
    for k,v in c_s.items():
        s+="{}: {}".format(k,v)
    return s


class PatternFinder(object):

    def __init__(self, max_pattern=1, trans_table = string_to_uc_level2, trans_func=translate_char):
        self._max_patterns=max_pattern
        self._patterns = []
        self._count=0
        self._value_length=set([])
        self._char_count={}
        self.compress_strategy = CompressStrategy.ALL_AFTER
        self.trans_func = trans_func
        self.trans_table = trans_table
        self.translate = lambda x: self.trans_func(x, trans_table=self.trans_table)

    def free_slots(self):
        return len(self._patterns)<self._max_patterns

    def add(self, value):
        log.debug("ADD", value=value)

        if len(value.strip())== 0:
            log.info("Empty value, stop")
            return


        ivpat = Pattern(value, translate=self.translate)
        if self.free_slots():
            log.debug("FREE SLOTS", pattern=ivpat)
            self._patterns.append( ivpat )
        else:
            log.debug("NO FREE SLOTS", pattern=ivpat)

            #find closest pattern -> returns pos and alignment
            pos, alignment = self.closest_pattern_to(ivpat)
            log.debug(" [BEST ALIGNMENT] Best alignment for %s is %s with ALIGN:%s", ivpat, self._patterns[pos], alignment.data['best'])
            if alignment.data['best']['identity'] != 100:

                # TODO: We need to decide at what stage we try to merge!!!
                cur_identity=alignment.data['best']['identity']
                if self.compress_before(cur_identity):
                    if self.free_slots():
                        log.debug(" We have free slots after compressing: adding empty pattern %s", ivpat)
                        self._patterns.append(ivpat)
                        pos, alignment=None,None
                    else:
                        log.debug(" No free slots for %s", ivpat)

                        # find closest pattern -> returns pos and alignment
                        pos, alignment = self.closest_pattern_to(ivpat)
                        log.debug(" Best alignment after compressing for input %s is for %s with ALIGN:%s", ivpat, self._patterns[pos],
                                 alignment.data['best'])


            if pos is not None and alignment:
                #get pattern with best alignment score
                p = self._patterns[pos]

                p.update_with_alignment(alignment)

                self.compress_after(pos)

        self._value_length.add(len(value))
        for c in value:
            self._char_count.setdefault(c,0)
            self._char_count[c]+=1
        self._count+=1
        log.debug("--> %s", self)

    def compress_before(self, identity)->bool:
        """
        Try to compress the patterns before we insert a new one
        To do so, we need to compare the alignment between existing patterns.
        since alignments should be transitive, it should not matter if we do alpha-beta or beta-alpha

        rank the patterns based on their length

        :param identity:
        :return:
        """

        if len(self._patterns) == 1:
            log.debug("[COMP_BEFORE] Only one pattern, Nothing to compress")
            return False
        log.debug("[COMP_BEFORE] Check if we can compress pattern groups with identiy >%s",identity)

        def compare_patterns(a,b):
            return len(a[1].symbol) - len(b[1].symbol)

        _s_al = sorted(enumerate(self._patterns), key=functools.cmp_to_key(compare_patterns), reverse=True)

        import itertools
        _al=[]
        _comb=[]
        for a, b in itertools.combinations(_s_al, 2):
            _comb.append((a[0],b[0]))
            alignment = Alignment(a[1], b[1], translate=self.translate)
            _al.append(alignment)


        _s_al = sorted(enumerate(_al), key=functools.cmp_to_key(compare), reverse=True)
        s=""
        for k in _s_al:
            s+="\n"+"  pos:{} {}".format(k[0],reindent(k[1],5))
        log.debug("[COMP_BEFORE] computed %s alignments %s", len(_s_al),s)

        merged=False
        best_align=_s_al[0][1]
        if best_align.best()['identity']>identity:
            a_idx, b_idx= _comb[_s_al[0][0]]
            p_alpha = self._patterns[a_idx]
            p_beta = self._patterns[b_idx]
            log.debug("[COMP_BEFORE] We can merge two patterns %s %s",p_alpha, p_beta)

            p_alpha.merge_with_pattern(p_beta, best_align)

            self._patterns[a_idx] = p_alpha
            log.debug("[COMP_BEFORE] Removing pattern at index %s %s", b_idx,self._patterns[b_idx])
            del (self._patterns[b_idx])
            merged = True
        return merged

    def compress_after(self, idx):
        """
        call this function whenever a new merge was done.
        Check if any untouched pattern could be merged in the new pattern
        :return:
        """
        if len(self._patterns) == 1:
            log.debug("[COMP] Only one pattern, Nothing to compress")
            return
        log.debug("[COMP] Check if we can compress pattern groups")

        _al=[]
        _pat=self._patterns[idx]
        for i,_p in enumerate(self._patterns):
            if i != idx:
                #exclude idx
                alignment = Alignment(_pat, _p, translate=self.translate)
                _al.append(alignment)
            else:
                _al.append(None)


        _s_al = sorted(enumerate(_al), key=functools.cmp_to_key(compare), reverse=True)

        log.debug("[COMP] Compared %s to %s patterns", _pat, len(_al))
        s = ""
        for k in _s_al:
            s += "\n" + "  pos:{} {}".format(k[0], reindent(k[1], 5))
        log.debug("[COMP_BEFORE] computed %s alignments %s", len(_s_al), s)


        _idx, alignment = _s_al[0]

        log.debug("[COMP] Best alignment for input %s is for %s with ALIGN:%s", _pat, self._patterns[_idx],
                     alignment.data['best'])
        id_to_del=[]
        for _idx, alignment in _s_al:
            if alignment and alignment.data['best']['identity'] == 100:

                p_alpha = self._patterns[idx]

                p_beta=self._patterns[_idx]
                p_alpha.merge_with_pattern(p_beta, alignment)
                self._patterns[idx] = p_alpha

                id_to_del.append(_idx)

        for i in sorted(id_to_del, reverse=True):
            log.debug("[COMP_AFTER] Removing pattern at index %s %s", i, self._patterns[i])
            del (self._patterns[i])



    def closest_pattern_to(self, value, excludePos=None):
        """
        compuates the closest pattern, with closest as having the higest identiy or if equals highest score

        :param value: string value to add
        :param excludePos: optional parameter to exclude a certain existing pattern
        :return: position of closest pattern and the computed alignment
        """
        log.debug("  >{:-^30}<".format(' CLOSEST PATTERN '))
        log.debug("  Find closest pattern to %s (excludePos=%s)",value, excludePos)
        _al= []
        for i, _pat in enumerate(self._patterns):

            if excludePos is None or i != excludePos:
                alignment = Alignment(_pat, value, translate=self.translate)
                _al.append( alignment )
            else:
                _al.append(None)


        #sort, define sort function for alignment objects

        _s_al= sorted(enumerate(_al), key=functools.cmp_to_key(compare), reverse=True)


        s=""
        for k in _s_al:
            s+="\n"+reindent(k[1],4)
        log.debug("  Compared %s to %s patterns %s", value, len(_al),s)


        return _s_al[0]

    def info(self):
        s = "{:*>20} {} {:*<20}\n" \
            "  {:6>} elements\n" \
            " {:->2} {}/{} Groups {:-<10}".format("", self.__class__.__name__, "",
                                                  self._count,
                                                  "", len(self._patterns), self._max_patterns, "")
        c=0
        for i, p in enumerate(sorted(self._patterns, reverse=True)):
            s += "\n {:>2} {}".format(i, p)
            c+=p._count
        s+="\n -- sum: {}".format(c)
        return s



    def __str__(self):
        s="#{}[#{}, {}/{}]".format(self.__class__.__name__, self._count,len(self._patterns),self._max_patterns)

        for i,p in enumerate(sorted(self._patterns, reverse=True)):
            s+=" ${}-{} ".format(i,p)
        return s

    def __repr__(self):
        s = "\n#{:*>20} {} {:*<20}\n" \
            "#  {:6>} values added\n" \
            "# {:->2} {}/{} Groups {:-<10}".format("", self.__class__.__name__, "",
                                                  self._count,
                                                  "", len(self._patterns), self._max_patterns, "")
        for i, p in enumerate(sorted(self._patterns, reverse=True)):
            s += "\n# {:>2}: {}".format(i, repr(p))

        return s



@timer(key='pattern2')
def pattern(items, max_pattern=3):
    pm = PatternFinder(max_pattern = max_pattern, trans_table = string_to_uc_level2, trans_func=translate_char)
    for value in items:
        pm.add(value)
    return pm





