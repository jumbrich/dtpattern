
from __future__ import print_function

import warnings


from dtpattern.timer import timer, Timer
from dtpattern.unicode_translate.uc_models import FIX_SYMB, OPT_SYMB, SYMB_GROUP

MAX_ALIGNMENTS = 1000   # maximum alignments recovered in traceback

from multipledispatch import dispatch


score_matrix={
    'match':5,
    'mismatch':-4,
    'csetmatch':1,
    'OPT_SYMBional_match':1

}

class identity_match2(object):
    """Create a match function for use in an alignment.

    match and mismatch are the scores to give when two residues are equal
    or unequal.  By default, match is 1 and mismatch is 0.
    """

    def __init__(self, translate, match=1, mismatch=0, csetmatch=1, optional_match=1):
        """Initialize the class."""
        self.translate = translate
        self.match = match
        self.mismatch = mismatch
        self.csetmatch = csetmatch
        self.optional_match=optional_match


    @dispatch(str, str)
    def identity_score(self, alpha, beta):
        return self.match if alpha == beta else self.mismatch


    @dispatch(FIX_SYMB, str)
    def identity_score(self, alpha, beta):
        t= self.translate(beta)
        if t == alpha.symbol:
            return self.csetmatch
        return self.mismatch

    @dispatch(str, FIX_SYMB)
    def identity_score(self, alpha, beta):
        return self.identity_score(beta,alpha)

    @dispatch(FIX_SYMB, FIX_SYMB)
    def identity_score(self, alpha, beta):
        if alpha.symbol==beta.symbol:
            return self.csetmatch
        return self.mismatch



    @dispatch(object, OPT_SYMB)
    def identity_score(self, alpha, beta):
         score = self.identity_score(alpha, beta.symbol)
         return score-1 if score >0 else score

    @dispatch(OPT_SYMB, object)
    def identity_score(self, alpha, beta):
         score= self.identity_score(alpha.symbol, beta)
         return score - 1 if score > 0 else score

    @dispatch(SYMB_GROUP, object)
    def identity_score(self, alpha, beta):
        return max([self.identity_score(sym, beta) for sym in alpha.symbols])


    @dispatch(SYMB_GROUP, OPT_SYMB)
    def identity_score(self, alpha, beta):
        return max([self.identity_score(sym, beta) for sym in alpha.symbols])

    @dispatch(OPT_SYMB, OPT_SYMB)
    def identity_score(self, alpha, beta):
        return max([self.identity_score(alpha,sym) for sym in beta.symbols])

    # @dispatch(tuple, tuple)
    # def identity_score(self, alpha, beta):
    #     score = self.identity_score(alpha[0], beta[0])
    #     return score - 1 if score > 0 else score
    #
    # @dispatch(str, list)
    # def identity_score(self, alpha, beta):
    #     return self.csetmatch if translate(alpha) in beta else self.mismatch
    #
    #
    # @dispatch(list, str)
    # def identity_score(self, alpha, beta):
    #     return self.csetmatch if translate(beta) in alpha else self.mismatch
    #
    # ##OPT_SYMBIONAL PATTERNS
    # @dispatch(object, tuple)
    # def identity_score(self, alpha, beta):
    #     score = self.identity_score(alpha, beta[0])
    #     return score-1 if score >0 else score
    #
    # @dispatch(tuple, object)
    # def identity_score(self, alpha, beta):
    #     score= self.identity_score(alpha[0], beta)
    #     return score - 1 if score > 0 else score

    def __call__(self, alpha, beta):
        score= self.identity_score(alpha,beta)
        return score

        # """Call a match function instance already created."""
        # if isinstance(alpha, str) and isinstance(beta, str):
        #     if alpha == beta:
        #         return self.match
        # elif isinstance(alpha, list) and isinstance(beta, list):
        #     if set(beta) < set(alpha):
        #         return self.match
        # elif isinstance(alpha, tuple) and isinstance(beta, tuple):
        #     ## assume for now that tuples have only one element and same length
        #     if alpha[0] == beta[0]:
        #         return self.match
        #
        # ## str vs list
        # elif isinstance(alpha, str) and  isinstance(beta, list):
        #     FIX_SYMB = translate(alpha)
        #     if FIX_SYMB in beta:
        #         return self.csetmatch
        # elif isinstance(alpha, list) and isinstance(beta, str):
        #     FIX_SYMB = translate(beta)
        #     if FIX_SYMB in alpha:
        #         return self.csetmatch
        #
        # # str vs tuple
        # elif isinstance(alpha, str) and  isinstance(beta, tuple):
        #     FIX_SYMB = translate(alpha)
        #     if len(FIX_SYMB)>0 and FIX_SYMB in beta[0]:
        #         return self.csetmatch
        # elif isinstance(alpha, tuple) and isinstance(beta, str):
        #     FIX_SYMB = translate(beta)
        #     if len(FIX_SYMB)>0 and FIX_SYMB in alpha[0]:
        #         return self.csetmatch
        #
        # # list vs tuple
        # elif isinstance(alpha, list) and isinstance(beta, tuple):
        #     if set([c for c in beta[0]]) < set(alpha):
        #         return self.match
        # elif isinstance(alpha, tuple) and isinstance(beta, list):
        #     if set(beta) < set([c for c in alpha[0]]):
        #         return self.match
        #
        # return self.mismatch



@timer(key='align_global')
def align_global(s1,s2, translate, match=5, csetmatch=4, optional_match=4, mismatch=4, gapopen=-15, gapextend=-1 ):
    pe=0
    default_params = [
        ('sequenceA', s1),('sequenceB',s2),
        ('match_fn', identity_match2(translate=translate,match=match, mismatch=mismatch, csetmatch=csetmatch,optional_match=optional_match)),
        ('gap_A_fn', affine_penalty(gapopen, gapextend, pe)),
        ('gap_B_fn', affine_penalty(gapopen, gapextend, pe)),
        ('penalize_extend_when_opening', 0),
        ('penalize_end_gaps', True),
        ('align_globally', True),
        ('gap_char', ['']),
        ('force_generic', 0),
        ('score_only', 0),
        ('one_alignment_only', 0),
    ]
    keywds={}
    for name, default in default_params:
        keywds[name] = keywds.get(name, default)
    value = keywds['penalize_end_gaps']
    try:
        n = len(value)
    except TypeError:
        keywds['penalize_end_gaps'] = tuple([value] * 2)
    else:
        assert n == 2

    return _align(**keywds)



class align(object):
    """Provide functions that do alignments.

    Alignment functions are called as:

      pairwise2.align.globalXX

    or

      pairwise2.align.localXX

    Where XX is a 2 character code indicating the match/mismatch parameters
    (first character, either x, m, d or c) and the gap penalty parameters
    (second character, either x, s, d, or c).

    For a detailed description read the main module's docstring (e.g.,
    type ``help(pairwise2)``).
    To see a description of the parameters for a function, please
    look at the docstring for the function, e.g. type
    ``help(pairwise2.align.localds``) at the Python prompt.
    """

    class alignment_function(object):
        """Callable class which impersonates an alignment function.

        The constructor takes the name of the function.  This class
        will decode the name of the function to figure out how to
        interpret the parameters.
        """

        # match code -> tuple of (parameters, docstring)
        match2args = {
            'x': ([], ''),
            'm': (['match', 'mismatch'],
                  "match is the score to given to identical characters.\n"
                  "mismatch is the score given to non-identical ones."),
            'd': (['match_dict'],
                  "match_dict is a dictionary where the keys are tuples\n"
                  "of pairs of characters and the values are the scores,\n"
                  "e.g. ('A', 'C') : 2.5."),
            'c': (['match_fn'],
                  "match_fn is a callback function that takes two "
                  "characters and returns the score between them."),
        }
        # penalty code -> tuple of (parameters, docstring)
        penalty2args = {
            'x': ([], ''),
            's': (['open', 'extend'],
                  "open and extend are the gap penalties when a gap is\n"
                  "opened and extended.  They should be negative."),
            'd': (['openA', 'extendA', 'openB', 'extendB'],
                  "openA and extendA are the gap penalties for sequenceA,\n"
                  "and openB and extendB for sequenceB.  The penalties\n"
                  "should be negative."),
            'c': (['gap_A_fn', 'gap_B_fn'],
                  "gap_A_fn and gap_B_fn are callback functions that takes\n"
                  "(1) the index where the gap is opened, and (2) the length\n"
                  "of the gap.  They should return a gap penalty."),
        }

        def __init__(self, name):
            """Check to make sure the name of the function is reasonable."""
            if name.startswith("global"):
                if len(name) != 8:
                    raise AttributeError("function should be globalXX")
            elif name.startswith("local"):
                if len(name) != 7:
                    raise AttributeError("function should be localXX")
            else:
                raise AttributeError(name)
            align_type, match_type, penalty_type = \
                name[:-2], name[-2], name[-1]
            try:
                match_args, match_doc = self.match2args[match_type]
            except KeyError:
                raise AttributeError("unknown match type %r" % match_type)
            try:
                penalty_args, penalty_doc = self.penalty2args[penalty_type]
            except KeyError:
                raise AttributeError("unknown penalty type %r" % penalty_type)

            # Now get the names of the parameters to this function.
            param_names = ['sequenceA', 'sequenceB']
            param_names.extend(match_args)
            param_names.extend(penalty_args)
            self.function_name = name
            self.align_type = align_type
            self.param_names = param_names

            self.__name__ = self.function_name
            # Set the doc string.
            doc = "%s(%s) -> alignments\n" % (
                self.__name__, ', '.join(self.param_names))
            if match_doc:
                doc += "\n%s\n" % match_doc
            if penalty_doc:
                doc += "\n%s\n" % penalty_doc
            doc += ("""\
\nalignments is a list of tuples (seqA, seqB, score, begin, end).
seqA and seqB are strings showing the alignment between the
sequences.  score is the score of the alignment.  begin and end
are indexes into seqA and seqB that indicate the where the
alignment occurs.
""")
            self.__doc__ = doc

        def decode(self, *args, **keywds):
            """Decode the arguments for the _align function.

            keywds will get passed to it, so translate the arguments
            to this function into forms appropriate for _align.
            """
            keywds = keywds.copy()
            if len(args) != len(self.param_names):
                raise TypeError("%s takes exactly %d argument (%d given)"
                                % (self.function_name, len(self.param_names),
                                   len(args)))
            i = 0
            while i < len(self.param_names):
                if self.param_names[i] in [
                   'sequenceA', 'sequenceB',
                   'gap_A_fn', 'gap_B_fn', 'match_fn']:
                    keywds[self.param_names[i]] = args[i]
                    i += 1
                elif self.param_names[i] == 'match':
                    assert self.param_names[i + 1] == 'mismatch'
                    match, mismatch = args[i], args[i + 1]
                    keywds['match_fn'] = identity_match(match, mismatch)
                    i += 2
                elif self.param_names[i] == 'match_dict':
                    keywds['match_fn'] = dictionary_match(args[i])
                    i += 1
                elif self.param_names[i] == 'open':
                    assert self.param_names[i + 1] == 'extend'
                    open, extend = args[i], args[i + 1]
                    pe = keywds.get('penalize_extend_when_opening', 0)
                    keywds['gap_A_fn'] = affine_penalty(open, extend, pe)
                    keywds['gap_B_fn'] = affine_penalty(open, extend, pe)
                    i += 2
                elif self.param_names[i] == 'openA':
                    assert self.param_names[i + 3] == 'extendB'
                    openA, extendA, openB, extendB = args[i:i + 4]
                    pe = keywds.get('penalize_extend_when_opening', 0)
                    keywds['gap_A_fn'] = affine_penalty(openA, extendA, pe)
                    keywds['gap_B_fn'] = affine_penalty(openB, extendB, pe)
                    i += 4
                else:
                    raise ValueError("unknown parameter %r"
                                     % self.param_names[i])

            # Here are the default parameters for _align.  Assign
            # these to keywds, unless already specified.
            pe = keywds.get('penalize_extend_when_opening', 0)
            default_params = [
                ('match_fn', identity_match(1, 0)),
                ('gap_A_fn', affine_penalty(0, 0, pe)),
                ('gap_B_fn', affine_penalty(0, 0, pe)),
                ('penalize_extend_when_opening', 0),
                ('penalize_end_gaps', self.align_type == 'global'),
                ('align_globally', self.align_type == 'global'),
                ('gap_char', ['']),
                ('force_generic', 0),
                ('score_only', 0),
                ('one_alignment_only', 0),
            ]
            for name, default in default_params:
                keywds[name] = keywds.get(name, default)
            value = keywds['penalize_end_gaps']
            try:
                n = len(value)
            except TypeError:
                keywds['penalize_end_gaps'] = tuple([value] * 2)
            else:
                assert n == 2
            return keywds

        def __call__(self, *args, **keywds):
            """Call the alignment instance already created."""
            keywds = self.decode(*args, **keywds)
            return _align(**keywds)

    def __getattr__(self, attr):
        """Call alignment_function() to check and decode the attributes."""
        # The following 'magic' is needed to rewrite the class docstring
        # dynamically:
        wrapper = self.alignment_function(attr)
        wrapper_type = type(wrapper)
        wrapper_dict = wrapper_type.__dict__.copy()
        wrapper_dict['__doc__'] = wrapper.__doc__
        new_alignment_function = type('alignment_function', (object,),
                                      wrapper_dict)

        return new_alignment_function(attr)


align = align()

@timer(key='_align')
def _align(sequenceA, sequenceB, match_fn, gap_A_fn, gap_B_fn,
           penalize_extend_when_opening, penalize_end_gaps,
           align_globally, gap_char, force_generic, score_only,
           one_alignment_only):
    """Return optimal alignments between two sequences (PRIVATE).

    This method either returns a list of optimal alignments (with the same
    score) or just the optimal score.
    """
    if not sequenceA or not sequenceB:
        return []
    try:
        sequenceA + gap_char
        sequenceB + gap_char
    except TypeError:
        raise TypeError('both sequences must be of the same type, either '
                        'string/sequence object or list. Gap character must '
                        'fit the sequence type (string or list)')

    if not isinstance(sequenceA, list):
        sequenceA = str(sequenceA)
    if not isinstance(sequenceB, list):
        sequenceB = str(sequenceB)
    if not align_globally and (penalize_end_gaps[0] or penalize_end_gaps[1]):
        warnings.warn('"penalize_end_gaps" should not be used in local '
                      'alignments. The resulting score may be wrong.',
                      ValueError)

    if (not force_generic) and isinstance(gap_A_fn, affine_penalty) \
       and isinstance(gap_B_fn, affine_penalty):
        open_A, extend_A = gap_A_fn.open, gap_A_fn.extend
        open_B, extend_B = gap_B_fn.open, gap_B_fn.extend
        with Timer(key="_score_fast"):
            matrices = _make_score_matrix_fast(
                sequenceA, sequenceB, match_fn, open_A, extend_A, open_B,
                extend_B, penalize_extend_when_opening, penalize_end_gaps,
                align_globally, score_only)
    else:
        matrices = _make_score_matrix_generic(
            sequenceA, sequenceB, match_fn, gap_A_fn, gap_B_fn,
            penalize_end_gaps, align_globally, score_only)
    score_matrix, trace_matrix = matrices

    # print("SCORE %s" % print_matrix(score_matrix))
    # print("TRACEBACK %s" % print_matrix(trace_matrix))

    # Look for the proper starting point. Get a list of all possible
    # starting points.
    starts = _find_start(score_matrix, align_globally)
    # Find the highest score.
    best_score = max([_[0] for _ in starts])

    # If they only want the score, then return it.
    if score_only:
        return best_score

    tolerance = 0  # XXX do anything with this?
    # Now find all the positions within some tolerance of the best
    # score.
    starts = [(score, pos) for score, pos in starts
              if rint(abs(score - best_score)) <= rint(tolerance)]

    # Recover the alignments and return them.
    alignments = _recover_alignments(sequenceA, sequenceB, starts,
                                     score_matrix, trace_matrix,
                                     align_globally, gap_char,
                                     one_alignment_only, gap_A_fn, gap_B_fn)
    if not alignments:
        # This may happen, see recover_alignments for explanation
        score_matrix, trace_matrix = _reverse_matrices(score_matrix,
                                                       trace_matrix)
        starts = [(z, (y, x)) for z, (x, y) in starts]
        alignments = _recover_alignments(sequenceB, sequenceA, starts,
                                         score_matrix, trace_matrix,
                                         align_globally, gap_char,
                                         one_alignment_only, gap_B_fn,
                                         gap_A_fn, reverse=True)
    return alignments

@timer(key='_m_score_matrix')
def _make_score_matrix_generic(sequenceA, sequenceB, match_fn, gap_A_fn,
                               gap_B_fn, penalize_end_gaps, align_globally,
                               score_only):
    """Generate a score and traceback matrix (PRIVATE).

    This implementation according to Needleman-Wunsch allows the usage of
    general gap functions and is rather slow. It is automatically called if
    you define your own gap functions. You can force the usage of this method
    with ``force_generic=True``.
    """
    # Create the score and traceback matrices. These should be in the
    # shape:
    # sequenceA (down) x sequenceB (across)
    lenA, lenB = len(sequenceA), len(sequenceB)
    score_matrix, trace_matrix = [], []
    for i in range(lenA + 1):
        score_matrix.append([None] * (lenB + 1))
        if not score_only:
            trace_matrix.append([None] * (lenB + 1))

    # Initialize first row and column with gap scores. This is like opening up
    # i gaps at the beginning of sequence A or B.
    for i in range(lenA + 1):
        if penalize_end_gaps[1]:  # [1]:gap in sequence B
            score = gap_B_fn(0, i)
        else:
            score = 0
        score_matrix[i][0] = score
    for i in range(lenB + 1):
        if penalize_end_gaps[0]:  # [0]:gap in sequence A
            score = gap_A_fn(0, i)
        else:
            score = 0
        score_matrix[0][i] = score

    # Fill in the score matrix.  Each position in the matrix
    # represents an alignment between a character from sequence A to
    # one in sequence B.  As I iterate through the matrix, find the
    # alignment by choose the best of:
    #    1) extending a previous alignment without gaps
    #    2) adding a gap in sequenceA
    #    3) adding a gap in sequenceB
    for row in range(1, lenA + 1):
        for col in range(1, lenB + 1):
            # First, calculate the score that would occur by extending
            # the alignment without gaps.
            nogap_score = score_matrix[row - 1][col - 1] + \
                match_fn(sequenceA[row - 1], sequenceB[col - 1])

            # Try to find a better score by opening gaps in sequenceA.
            # Do this by checking alignments from each column in the row.
            # Each column represents a different character to align from,
            # and thus a different length gap.
            # Although the gap function does not distinguish between opening
            # and extending a gap, we distinguish them for the backtrace.
            if not penalize_end_gaps[0] and row == lenA:
                row_open = score_matrix[row][col - 1]
                row_extend = max([score_matrix[row][x] for x in range(col)])
            else:
                row_open = score_matrix[row][col - 1] + gap_A_fn(row, 1)
                row_extend = max([score_matrix[row][x] + gap_A_fn(row, col - x)
                                  for x in range(col)])

            # Try to find a better score by opening gaps in sequenceB.
            if not penalize_end_gaps[1] and col == lenB:
                col_open = score_matrix[row - 1][col]
                col_extend = max([score_matrix[x][col] for x in range(row)])
            else:
                col_open = score_matrix[row - 1][col] + gap_B_fn(col, 1)
                col_extend = max([score_matrix[x][col] + gap_B_fn(col, row - x)
                                  for x in range(row)])

            best_score = max(nogap_score, row_open, row_extend, col_open,
                             col_extend)
            if not align_globally and best_score < 0:
                score_matrix[row][col] = 0
            else:
                score_matrix[row][col] = best_score

            # The backtrace is encoded binary. See _make_score_matrix_fast
            # for details.
            if not score_only:
                trace_score = 0
                if rint(nogap_score) == rint(best_score):
                    trace_score += 2
                if rint(row_open) == rint(best_score):
                    trace_score += 1
                if rint(row_extend) == rint(best_score):
                    trace_score += 8
                if rint(col_open) == rint(best_score):
                    trace_score += 4
                if rint(col_extend) == rint(best_score):
                    trace_score += 16
                trace_matrix[row][col] = trace_score

    return score_matrix, trace_matrix

@timer(key='_m_score_fast')
def _make_score_matrix_fast(sequenceA, sequenceB, match_fn, open_A, extend_A,
                            open_B, extend_B, penalize_extend_when_opening,
                            penalize_end_gaps, align_globally, score_only):
    """Generate a score and traceback matrix according to Gotoh (PRIVATE).

    This is an implementation of the Needleman-Wunsch dynamic programming
    algorithm as modified by Gotoh, implementing affine gap penalties.
    In short, we have three matrices, holding scores for alignments ending
    in (1) a match/mismatch, (2) a gap in sequence A, and (3) a gap in
    sequence B, respectively. However, we can combine them in one matrix,
    which holds the best scores, and store only those values from the
    other matrices that are actually used for the next step of calculation.
    The traceback matrix holds the positions for backtracing the alignment.
    """
    first_A_gap = calc_affine_penalty(1, open_A, extend_A,
                                      penalize_extend_when_opening)
    first_B_gap = calc_affine_penalty(1, open_B, extend_B,
                                      penalize_extend_when_opening)

    # Create the score and traceback matrices. These should be in the
    # shape:
    # sequenceA (down) x sequenceB (across)
    lenA, lenB = len(sequenceA), len(sequenceB)
    score_matrix, trace_matrix = [], []
    for i in range(lenA + 1):
        score_matrix.append([None] * (lenB + 1))
        if not score_only:
            trace_matrix.append([None] * (lenB + 1))

    # Initialize first row and column with gap scores. This is like opening up
    # i gaps at the beginning of sequence A or B.
    for i in range(lenA + 1):
        if penalize_end_gaps[1]:  # [1]:gap in sequence B
            score = calc_affine_penalty(i, open_B, extend_B,
                                        penalize_extend_when_opening)
        else:
            score = 0
        score_matrix[i][0] = score
    for i in range(lenB + 1):
        if penalize_end_gaps[0]:  # [0]:gap in sequence A
            score = calc_affine_penalty(i, open_A, extend_A,
                                        penalize_extend_when_opening)
        else:
            score = 0
        score_matrix[0][i] = score

    # Now initialize the col 'matrix'. Actually this is only a one dimensional
    # list, since we only need the col scores from the last row.
    col_score = [0]  # Best score, if actual alignment ends with gap in seqB
    for i in range(1, lenB + 1):
        col_score.append(calc_affine_penalty(i, 2 * open_B, extend_B,
                                             penalize_extend_when_opening))

    # The row 'matrix' is calculated on the fly. Here we only need the actual
    # score.
    # Now, filling up the score and traceback matrices:
    for row in range(1, lenA + 1):
        row_score = calc_affine_penalty(row, 2 * open_A, extend_A,
                                        penalize_extend_when_opening)
        for col in range(1, lenB + 1):
            # Calculate the score that would occur by extending the
            # alignment without gaps.
            nogap_score = score_matrix[row - 1][col - 1] + \
                match_fn(sequenceA[row - 1], sequenceB[col - 1])

            # Check the score that would occur if there were a gap in
            # sequence A. This could come from opening a new gap or
            # extending an existing one.
            # A gap in sequence A can also be opened if it follows a gap in
            # sequence B:  A-
            #              -B
            if not penalize_end_gaps[0] and row == lenA:
                row_open = score_matrix[row][col - 1]
                row_extend = row_score
            else:
                row_open = score_matrix[row][col - 1] + first_A_gap
                row_extend = row_score + extend_A
            row_score = max(row_open, row_extend)

            # The same for sequence B:
            if not penalize_end_gaps[1] and col == lenB:
                col_open = score_matrix[row - 1][col]
                col_extend = col_score[col]
            else:
                col_open = score_matrix[row - 1][col] + first_B_gap
                col_extend = col_score[col] + extend_B
            col_score[col] = max(col_open, col_extend)

            best_score = max(nogap_score, col_score[col], row_score)
            if not align_globally and best_score < 0:
                score_matrix[row][col] = 0
            else:
                score_matrix[row][col] = best_score

            # Now the trace_matrix. The edges of the backtrace are encoded
            # binary: 1 = open gap in seqA, 2 = match/mismatch of seqA and
            # seqB, 4 = open gap in seqB, 8 = extend gap in seqA, and
            # 16 = extend gap in seqB. This values can be summed up.
            # Thus, the trace score 7 means that the best score can either
            # come from opening a gap in seqA (=1), pairing two characters
            # of seqA and seqB (+2=3) or opening a gap in seqB (+4=7).
            # However, if we only want the score we don't care about the trace.
            if not score_only:
                row_score_rint = rint(row_score)
                col_score_rint = rint(col_score[col])
                row_trace_score = 0
                col_trace_score = 0
                if rint(row_open) == row_score_rint:
                    row_trace_score += 1  # Open gap in seqA
                if rint(row_extend) == row_score_rint:
                    row_trace_score += 8  # Extend gap in seqA
                if rint(col_open) == col_score_rint:
                    col_trace_score += 4  # Open gap in seqB
                if rint(col_extend) == col_score_rint:
                    col_trace_score += 16  # Extend gap in seqB

                trace_score = 0
                best_score_rint = rint(best_score)
                if rint(nogap_score) == best_score_rint:
                    trace_score += 2  # Align seqA with seqB
                if row_score_rint == best_score_rint:
                    trace_score += row_trace_score
                if col_score_rint == best_score_rint:
                    trace_score += col_trace_score
                trace_matrix[row][col] = trace_score

    return score_matrix, trace_matrix

@timer(key='_rec_align')
def _recover_alignments(sequenceA, sequenceB, starts, score_matrix,
                        trace_matrix, align_globally, gap_char,
                        one_alignment_only, gap_A_fn, gap_B_fn, reverse=False):
    """Do the backtracing and return a list of alignments (PRIVATE).

    Recover the alignments by following the traceback matrix.  This
    is a recursive procedure, but it's implemented here iteratively
    with a stack.

    sequenceA and sequenceB may be sequences, including strings,
    lists, or list-like objects.  In order to preserve the type of
    the object, we need to use slices on the sequences instead of
    indexes.  For example, sequenceA[row] may return a type that's
    not compatible with sequenceA, e.g. if sequenceA is a list and
    sequenceA[row] is a string.  Thus, avoid using indexes and use
    slices, e.g. sequenceA[row:row+1].  Assume that client-defined
    sequence classes preserve these semantics.
    """
    lenA, lenB = len(sequenceA), len(sequenceB)
    ali_seqA, ali_seqB = sequenceA[0:0], sequenceB[0:0]
    tracebacks = []
    in_process = []

    for start in starts:
        score, (row, col) = start
        begin = 0
        if align_globally:
            end = None
        else:
            # Local alignments should start with a positive score!
            if score <= 0:
                continue
            # Local alignments should not end with a gap!:
            trace = trace_matrix[row][col]
            if (trace - trace % 2) % 4 == 2:  # Trace contains 'nogap', fine!
                trace_matrix[row][col] = 2
            # If not, don't start here!
            else:
                continue
            end = -max(lenA - row, lenB - col)
            if not end:
                end = None
            col_distance = lenB - col
            row_distance = lenA - row
            ali_seqA = ((col_distance - row_distance) * gap_char +
                        sequenceA[lenA - 1:row - 1:-1])
            ali_seqB = ((row_distance - col_distance) * gap_char +
                        sequenceB[lenB - 1:col - 1:-1])
        in_process += [(ali_seqA, ali_seqB, end, row, col, False,
                        trace_matrix[row][col])]
    while in_process and len(tracebacks) < MAX_ALIGNMENTS:
        # Although we allow a gap in seqB to be followed by a gap in seqA,
        # we don't want to allow it the other way round, since this would
        # give redundant alignments of type: A-  vs.  -A
        #                                    -B       B-
        # Thus we need to keep track if a gap in seqA was opened (col_gap)
        # and stop the backtrace (dead_end) if a gap in seqB follows.
        #
        # Attention: This may fail, if the gap-penalties for both strands are
        # different. In this case the second aligment may be the only optimal
        # alignment. Thus it can happen that no alignment is returned. For
        # this case a workaround was implemented, which reverses the input and
        # the matrices (this happens in _reverse_matrices) and repeats the
        # backtrace. The variable 'reverse' keeps track of this.
        dead_end = False
        ali_seqA, ali_seqB, end, row, col, col_gap, trace = in_process.pop()

        while (row > 0 or col > 0) and not dead_end:
            cache = (ali_seqA[:], ali_seqB[:], end, row, col, col_gap)

            # If trace is empty we have reached at least one border of the
            # matrix or the end of a local aligment. Just add the rest of
            # the sequence(s) and fill with gaps if necessary.
            if not trace:
                if col and col_gap:
                    dead_end = True
                else:
                    ali_seqA, ali_seqB = _finish_backtrace(
                        sequenceA, sequenceB, ali_seqA, ali_seqB,
                        row, col, gap_char)
                break
            elif trace % 2 == 1:  # = row open = open gap in seqA
                trace -= 1
                if col_gap:
                    dead_end = True
                else:
                    col -= 1
                    ali_seqA.append(gap_char[0])
                    ali_seqB.append(sequenceB[col:col + 1][0])
                    col_gap = False
            elif trace % 4 == 2:  # = match/mismatch of seqA with seqB
                trace -= 2
                row -= 1
                col -= 1
                ali_seqA.append(sequenceA[row:row + 1][0])
                ali_seqB.append(sequenceB[col:col + 1][0])
                col_gap = False
            elif trace % 8 == 4:  # = col open = open gap in seqB
                trace -= 4
                row -= 1
                ali_seqA.append(sequenceA[row:row + 1][0])
                ali_seqB.append(gap_char[0])
                col_gap = True
            elif trace in (8, 24):  # = row extend = extend gap in seqA
                trace -= 8
                if col_gap:
                    dead_end = True
                else:
                    col_gap = False
                    # We need to find the starting point of the extended gap
                    x = _find_gap_open(sequenceA, sequenceB, ali_seqA,
                                       ali_seqB, end, row, col, col_gap,
                                       gap_char, score_matrix, trace_matrix,
                                       in_process, gap_A_fn, col, row, 'col')
                    ali_seqA, ali_seqB, row, col, in_process, dead_end = x
            elif trace == 16:  # = col extend = extend gap in seqB
                trace -= 16
                col_gap = True
                x = _find_gap_open(sequenceA, sequenceB, ali_seqA, ali_seqB,
                                   end, row, col, col_gap, gap_char,
                                   score_matrix, trace_matrix, in_process,
                                   gap_B_fn, row, col, 'row')
                ali_seqA, ali_seqB, row, col, in_process, dead_end = x

            if trace:  # There is another path to follow...
                cache += (trace,)
                in_process.append(cache)
            trace = trace_matrix[row][col]
            if not align_globally and score_matrix[row][col] <= 0:
                begin = max(row, col)
                trace = 0
        if not dead_end:
            if not reverse:
                tracebacks.append((ali_seqA[::-1], ali_seqB[::-1], score,
                                   begin, end))
            else:
                tracebacks.append((ali_seqB[::-1], ali_seqA[::-1], score,
                                   begin, end))
            if one_alignment_only:
                break
    return _clean_alignments(tracebacks)


def _find_start(score_matrix, align_globally):
    """Return a list of starting points (score, (row, col)) (PRIVATE).

    Indicating every possible place to start the tracebacks.
    """
    nrows, ncols = len(score_matrix), len(score_matrix[0])
    # In this implementation of the global algorithm, the start will always be
    # the bottom right corner of the matrix.
    if align_globally:
        starts = [(score_matrix[-1][-1], (nrows - 1, ncols - 1))]
    else:
        starts = []
        for row in range(nrows):
            for col in range(ncols):
                score = score_matrix[row][col]
                starts.append((score, (row, col)))
    return starts


def _reverse_matrices(score_matrix, trace_matrix):
    """Reverse score and trace matrices (PRIVATE)."""
    reverse_score_matrix = []
    reverse_trace_matrix = []
    reverse_trace = {1: 4, 2: 2, 3: 6, 4: 1, 5: 5, 6: 3, 7: 7, 8: 16, 9: 20,
                     10: 18, 11: 22, 12: 17, 13: 21, 14: 19, 15: 23, 16: 8,
                     17: 12, 18: 10, 19: 14, 20: 9, 21: 13, 22: 11, 23: 15,
                     24: 24, 25: 28, 26: 26, 27: 30, 28: 25, 29: 29, 30: 27,
                     31: 31, None: None}
    for col in range(len(score_matrix[0])):
        new_score_row = []
        new_trace_row = []
        for row in range(len(score_matrix)):
            new_score_row.append(score_matrix[row][col])
            new_trace_row.append(reverse_trace[trace_matrix[row][col]])
        reverse_score_matrix.append(new_score_row)
        reverse_trace_matrix.append(new_trace_row)
    return reverse_score_matrix, reverse_trace_matrix


def _clean_alignments(alignments):
    """Take a list of alignments and return a cleaned version (PRIVATE).

    Remove duplicates, make sure begin and end are set correctly, remove
    empty alignments.
    """
    unique_alignments = []
    for align in alignments:
        if align not in unique_alignments:
            unique_alignments.append(align)
    i = 0
    while i < len(unique_alignments):
        seqA, seqB, score, begin, end = unique_alignments[i]
        # Make sure end is set reasonably.
        if end is None:   # global alignment
            end = len(seqA)
        elif end < 0:
            end = end + len(seqA)
        # If there's no alignment here, get rid of it.
        if begin >= end:
            del unique_alignments[i]
            continue
        unique_alignments[i] = seqA, seqB, score, begin, end
        i += 1
    return unique_alignments


def _finish_backtrace(sequenceA, sequenceB, ali_seqA, ali_seqB, row, col,
                      gap_char):
    """Add remaining sequences and fill with gaps if necessary (PRIVATE)."""
    if row:
        ali_seqA+= [c for c in sequenceA[row - 1::-1]]
        #ali_seqA.append(sequenceA[row - 1::-1])
    if col:
        ali_seqB+=[c for c in sequenceB[col - 1::-1]] ## remaining sequences shoudl be added as lists not concatinated
        #ali_seqB.append(sequenceB[col - 1::-1]) ## remaining sequences shoudl be added as lists not concatinated
    if row > col:
            ali_seqB += [gap_char[0] for i in range(0, (len(ali_seqA) - len(ali_seqB)))]
            #ali_seqB.append(gap_char * (len(ali_seqA) - len(ali_seqB)))
    elif col > row:
            ali_seqA += [gap_char[0] for i in range(0, (len(ali_seqB) - len(ali_seqA)))]
            #ali_seqA.append(gap_char * (len(ali_seqB) - len(ali_seqA)))
    return ali_seqA, ali_seqB


def _find_gap_open(sequenceA, sequenceB, ali_seqA, ali_seqB, end, row, col,
                   col_gap, gap_char, score_matrix, trace_matrix, in_process,
                   gap_fn, target, index, direction):
    """Find the starting point(s) of the extended gap (PRIVATE)."""
    dead_end = False
    target_score = score_matrix[row][col]
    for n in range(target):
        if direction == 'col':
            col -= 1
            ali_seqA.append(gap_char[0])
            ali_seqB.append(sequenceB[col:col + 1][0])
        else:
            row -= 1
            ali_seqA.append(sequenceA[row:row + 1][0])
            ali_seqB.append(gap_char[0])
        actual_score = score_matrix[row][col] + gap_fn(index, n + 1)
        if rint(actual_score) == rint(target_score) and n > 0:
            if not trace_matrix[row][col]:
                break
            else:
                in_process.append((ali_seqA[:], ali_seqB[:], end, row, col,
                                   col_gap, trace_matrix[row][col]))
        if not trace_matrix[row][col]:
            dead_end = True
    return ali_seqA, ali_seqB, row, col, in_process, dead_end


_PRECISION = 1000


def rint(x, precision=_PRECISION):
    """Print number with declared precision."""
    return int(x * precision + 0.5)


class identity_match(object):
    """Create a match function for use in an alignment.

    match and mismatch are the scores to give when two residues are equal
    or unequal.  By default, match is 1 and mismatch is 0.
    """

    def __init__(self, match=1, mismatch=0):
        """Initialize the class."""
        self.match = match
        self.mismatch = mismatch

    def __call__(self, charA, charB):
        """Call a match function instance already created."""
        if charA == charB:
            return self.match
        return self.mismatch


class dictionary_match(object):
    """Create a match function for use in an alignment.

    Attributes:
     - score_dict     - A dictionary where the keys are tuples (residue 1,
       residue 2) and the values are the match scores between those residues.
     - FIX_SYMBmetric      - A flag that indicates whether the scores are FIX_SYMBmetric.

    """

    def __init__(self, score_dict, FIX_SYMBmetric=1):
        """Initialize the class."""
        self.score_dict = score_dict
        self.FIX_SYMBmetric = FIX_SYMBmetric

    def __call__(self, charA, charB):
        """Call a dictionary match instance already created."""
        if self.FIX_SYMBmetric and (charA, charB) not in self.score_dict:
            # If the score dictionary is FIX_SYMBmetric, then look up the
            # score both ways.
            charB, charA = charA, charB
        return self.score_dict[(charA, charB)]


class affine_penalty(object):
    """Create a gap function for use in an alignment."""

    def __init__(self, open, extend, penalize_extend_when_opening=0):
        """Initialize the class."""
        if open > 0 or extend > 0:
            raise ValueError("Gap penalties should be non-positive.")
        if not penalize_extend_when_opening and (extend < open):
            raise ValueError("Gap opening penalty should be higher than " +
                             "gap extension penalty (or equal)")
        self.open, self.extend = open, extend
        self.penalize_extend_when_opening = penalize_extend_when_opening

    def __call__(self, index, length):
        """Call a gap function instance already created."""
        return calc_affine_penalty(
            length, self.open, self.extend, self.penalize_extend_when_opening)


def calc_affine_penalty(length, open, extend, penalize_extend_when_opening):
    """Calculate a penality score for the gap function."""
    if length <= 0:
        return 0
    penalty = open + extend * length
    if not penalize_extend_when_opening:
        penalty -= extend
    return penalty


def print_matrix(matrix):
    """Print out a matrix for debugging purposes."""
    # Transpose the matrix and get the length of the values in each column.
    matrixT = [[] for x in range(len(matrix[0]))]
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrixT[j].append(len(str(matrix[i][j])))
    ndigits = [max(x) for x in matrixT]
    for i in range(len(matrix)):
        # Using string formatting trick to add leading spaces,
        print(" ".join("%*s " % (ndigits[j], matrix[i][j])
                       for j in range(len(matrix[i]))))



class equals(object):
    """Create a match function for use in an alignment.

    match and mismatch are the scores to give when two residues are equal
    or unequal.  By default, match is 1 and mismatch is 0.
    """

    def __init__(self, translate):
        """Initialize the class."""
        self.translate = translate

    @dispatch(str, str)
    def _equals(self, alpha, beta):
        return alpha == beta

    @dispatch(FIX_SYMB, str)
    def _equals(self, alpha, beta):
        t = self.translate(beta)
        return alpha.symbol == t

    @dispatch(str, FIX_SYMB)
    def _equals(self, alpha, beta):
        return self._equals(beta, alpha)

    @dispatch(FIX_SYMB, FIX_SYMB)
    def _equals(self, alpha, beta):
        return alpha.symbol == beta.symbol




    @dispatch(object, OPT_SYMB)
    def _equals(self, alpha, beta):
        return self._equals(alpha, beta.symbol)

    @dispatch(OPT_SYMB, object)
    def _equals(self, alpha, beta):
        return self._equals(alpha.symbol, beta)

    @dispatch(SYMB_GROUP, object)
    def _equals(self, alpha, beta):
        return any([self._equals(sym, beta) for sym in alpha.symbols])

    @dispatch(SYMB_GROUP, OPT_SYMB)
    def _equals(self, alpha, beta):
        return any([self._equals(sym, beta) for sym in alpha.symbols])

    @dispatch(OPT_SYMB, OPT_SYMB)
    def _equals(self, alpha, beta):
        return self._equals(beta,alpha)

    def __call__(self, alpha, beta):
        score= self._equals(alpha,beta)
        return score


#
# @dispatch(str,str)
# def equals(alpha, beta):
#     return alpha == beta
#
#
#
#
#
# def equals(alpha, beta):
#     """Call a match function instance already created."""
#     if isinstance(alpha, str) and isinstance(beta, str):
#         if alpha == beta:
#             return True
#
#
#     elif isinstance(alpha, list) and isinstance(beta, list):
#         if set(beta) == set(alpha):
#             return True
#     elif isinstance(alpha, tuple) and isinstance(beta, tuple):
#         ## assume for now that tuples have only one element and same length
#         if alpha[0] == beta[0]:
#             return True
#
#     ## str vs list
#     elif isinstance(alpha, str) and isinstance(beta, list):
#         FIX_SYMB = translate(alpha)
#         FIX_SYMB = '' if len(FIX_SYMB) == 0 else FIX_SYMB[0]
#         if FIX_SYMB in beta:
#             return True
#     elif isinstance(alpha, list) and isinstance(beta, str):
#         FIX_SYMB = translate(beta)
#
#         FIX_SYMB='' if len(FIX_SYMB)==0 else FIX_SYMB[0]
#
#         if FIX_SYMB in alpha:
#             return True
#
#     # str vs tuple
#     elif isinstance(alpha, str) and isinstance(beta, tuple):
#         FIX_SYMB = translate(alpha)
#         FIX_SYMB = '' if len(FIX_SYMB) == 0 else FIX_SYMB[0]
#         if len(str(FIX_SYMB))>0 and FIX_SYMB in beta[0]:
#             return True
#     elif isinstance(alpha, tuple) and isinstance(beta, str):
#         FIX_SYMB = translate(beta)
#         FIX_SYMB = '' if len(FIX_SYMB) == 0 else FIX_SYMB[0]
#         if len(str(FIX_SYMB))>0 and FIX_SYMB in alpha[0]:
#             return True
#
#     # list vs tuple
#     elif isinstance(alpha, list) and isinstance(beta, tuple):
#         if set([c for c in beta[0]]) < set(alpha):
#             return True
#     elif isinstance(alpha, tuple) and isinstance(beta, list):
#         if set(beta) < set([c for c in alpha[0]]):
#             return True
#
#     return False


def finalize(align1, align2,  score, begin, end, translate = None):

    _equals = equals(translate=translate)
    i, j = 0, 0

    # calcuate identity, score and aligned sequeces
    symbol = []

    identity = 0

    for i in range(0, len(align1)):
        # if two AAs are the same, then output the letter
        if _equals(align1[i], align2[i]):
            if align1[i] != align2[i]:
                symbol.append([align1[i], align2[i]])
            else:
                symbol.append(align1[i])
            identity = identity + 1


        # if they are not identical and none of them is gap
        elif align1[i] != align2[i] and align1[i] != '' and align2[i] != '':
            symbol.append([align1[i], align2[i]])
            found = 0

        # if one of them is a gap, output a space
        elif align1[i] == '' or align2[i] == '':
            symbol.append([align1[i], align2[i]])

    identity = float(identity) / len(align1) * 100

    return identity, score, align1, symbol, align2


def to_string(s):
    if isinstance(s, str):
        return "'{}'".format(s)
    if isinstance(s,list):
        _s='{}'

        if len(s)>1:
            _s="[{}]"
        _s_ = ''
        _s_+=",".join([to_string(c) for c in s])
        #for c in s:
        #    _s_ += to_string(c)
        #if len(s)==1:
        #    _s_ = '$'+_s_.replace("'","")
        return _s.format(_s_)
    if isinstance(s, tuple):
        return "{}{{{},{}}}".format(s[0],s[1],s[2])

def format_alignment2(identity, score, align1, FIX_SYMBbol, align2, indent=1,translate = None):

    _equals = equals(translate=translate)

    FIX_SYMB = [to_string(c) for c in FIX_SYMBbol]
    al1 = [to_string(c) for c in align1]
    al2 = [to_string(c) for c in align2]

    sal1,sal2,sFIX_SYMB,_m='','','',''
    for i, d in enumerate(zip(al1,  FIX_SYMB, al2)):
        a, s, b = d
        _ml= max([len(a),len(s),len(b)])
        sa="{:^"+str(_ml)+"}  "

        sal1 += sa.format(a)
        sFIX_SYMB += sa.format(s)
        sal2 += sa.format(b)

        if _equals(align1[i],align2[i]):
            _m += sa.format('=')
        elif a == "''" or b == "''":
            _m += sa.format('X')
        else:
            _m += sa.format('.')

    p= ((len(sal2)+5)//2) - 7
    s = "#{}- {} -{}" \
        "\n# score: {} ( {:2.2f}% identical)".format("*"*p,"ALIGNMENT", "*"*p,score, identity)
    s += "\n#{:^5} {}".format("a1:",sal1)
    s += "\n#{:^5} {}".format("", _m)
    s += "\n#{:^5} {}".format("a2:", sal2)
    s += "\n#{}".format('-'*(len(sal2)+5))
    s += "\n#{:^5} {}".format("=>", sFIX_SYMB)


    return "\n".join((indent * " ") + i for i in s.splitlines())
    #return reindentBlock(s,indend)
    #s = "{:-^40}\n" \
    #            " s1: {}\n" \
    #            " s2: {}\n" \
    #            "  a: {}\n" \
    #            "  identity: {:2.2f}% Score: {}".format("ALIGNMENT " + "", align1, align2, str(FIX_SYMBbol), identity,
    #                                                    score))

def format_alignment(align1, align2, score, begin, end):
    """Format the alignment prettily into a string.

    Since Biopython 1.71 identical matches are shown with a pipe
    character, mismatches as a dot, and gaps as a space.

    Note that spaces are also used at the start/end of a local
    alignment.

    Prior releases just used the pipe character to indicate the
    aligned region (matches, mismatches and gaps).
    """
    s = []
    s.append("%s\n" % align1)
    s.append(" " * begin)
    for a, b in zip(align1[begin:end], align2[begin:end]):
        if a == b:
            s.append("|")  # match
        elif a == '' or b == '':
            s.append(" ")  # gap
        else:
            s.append(".")  # mismatch
    s.append("\n")
    s.append("%s\n" % align2)
    s.append("  Score=%g\n" % score)
    return ''.join(s)


# Try and load C implementations of functions. If I can't,
# then throw a warning and use the pure Python implementations.
# The redefinition is deliberate, thus the no quality assurance
# flag for when using flake8:

try:
    from Bio.cpairwise2 import rint, _make_score_matrix_fast  # noqa
except ImportError:
    pass
    warnings.warn('Import of C module failed. Falling back to pure Python ' +
                  'implementation. This may be slooow...')



