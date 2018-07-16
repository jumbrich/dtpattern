from dtpattern.unicode_translate.uc_models import FIX_SYMB, SYMB_GROUP, OPT_SYMB
from multipledispatch import dispatch



class merge(object):
    """Create a match function for use in an alignment.

    match and mismatch are the scores to give when two residues are equal
    or unequal.  By default, match is 1 and mismatch is 0.
    """

    def __init__(self, translate):
        """Initialize the class."""
        self.translate = translate

    @dispatch(str, str)
    def _merge(self, alpha, beta):
        #a list with the unique cset symbols
        l = list(set([self.translate(alpha), self.translate(beta)]))
        return [FIX_SYMB(c) for c in l]

    @dispatch(FIX_SYMB, str)
    def _merge(self, alpha, beta):
        t = FIX_SYMB(self.translate(beta),1)
        return self._merge(alpha, t)

    @dispatch(str, FIX_SYMB)
    def _merge(self, alpha, beta):
       return self._merge(beta, alpha)

    @dispatch(FIX_SYMB, FIX_SYMB)
    def _merge(self, alpha, beta):
        if beta.symbol == alpha.symbol:
            return alpha
        else:
            return SYMB_GROUP([beta, alpha],1)

    @dispatch(SYMB_GROUP, str)
    def _merge(self, alpha, beta):
        t = FIX_SYMB(self.translate(beta), 1)

        m=[]
        for sym in alpha.symbols:
            _m= self._merge(sym, t)
            if isinstance(_m, SYMB_GROUP):
                m+=_m.symbols
            else:
                m.append(_m)
        return SYMB_GROUP(list(set(m)),1)



    def __call__(self, alpha, beta):
        score= self._merge(alpha,beta)
        return score
#
#
# @dispatch(list,list)
# def merge(alpha, beta):
#     return list(set(alpha+beta))
#
# @dispatch(list,str)
# def merge(alpha, beta):
#     """
#
#     :param alpha: cset symbols
#     :param beta: original character
#     :return: a list with the unique cset symbols
#     """
#     t = translate(beta)
#     return list(set(alpha + t))
#
# @dispatch(str,list)
# def merge(alpha, beta):
#     # same as list, str, just flip the variables
#     return merge(beta, alpha)
#
# @dispatch(tuple, str)
# def merge(alpha, beta):
#     """
#
#     :param alpha: tuple is an OPT_SYMBional pattern
#     :param beta:
#     :return:
#     """
#
#
#     a10 = alpha[0]
#
#     m= merge(a10, beta)
#
#     m = (m, alpha[1], alpha[2])
#     return m
#
# @dispatch(tuple, tuple)
# def merge(alpha, beta):
#
#     m = merge(alpha[0], beta[0])
#
#     m = (m, min(alpha[1],beta[1]), max(alpha[2],beta[2]))
#     return m
#
# @dispatch(list, tuple)
# def merge(alpha, beta):
#     b = beta[0]
#
#     m = merge(alpha, b)
#
#     m = (m, beta[1], beta[2])
#     return m
#
# @dispatch(tuple,list)
# def merge(alpha, beta):
#     return merge(beta, alpha)
#
#
# @dispatch(str, tuple)
# def merge(alpha, beta):
#     """
#
#     :param alpha:
#     :param beta: tuple is an OPT_SYMBional pattern
#     :return:
#     """
#     return merge(beta,alpha)
#
#     b = beta[0]
#
#     m= merge(alpha, b)
#
#     m = (m, beta[1], beta[2])
#     return m
