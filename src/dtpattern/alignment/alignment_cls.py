import functools


from dtpattern.alignment.alignment_list import align_global, finalize, format_alignment2
from dtpattern.timer import timer
from dtpattern.unicode_translate.uc_models import FIX_SYMB


class Alignment(object):

    def __init__(self, alpha, beta, translate=None, m=5, mm=-4, om=3, csetm=4,go=-15, ge=-1):

        self.alpha=alpha
        self.beta=beta
        self.data={}
        self.m=m
        self.mm=mm
        self.om=om
        self.go=go
        self.csetm=csetm
        self.ge=ge


        self.translate = translate


        self.find_best_alignment(alpha.symbol, beta.symbol)


    def best(self):
        return self.data['best'] if 'best' in self.data else None

    @timer(key='best_align')
    def find_best_alignment(self, alpha_list, beta_list):
        score_matrix={
            'match':self.m,
            'csetmatch':self.csetm,
            'optional_match':self.om,
            'mismatch': self.mm,
            'gapopen':self.go,
            'gapextend':self.ge
        }

        aligns = align_global(alpha_list, beta_list, self.translate, **score_matrix)
        identity, score, align1, symbol2, align2 = finalize(*aligns[0], translate=self.translate)

        self.data['raw']={ 'score':score, 'identity':identity,
                            'align1':align1,'align2':align2, 'symbol':symbol2
                         }
        if 0< identity < 100:
            #identtiy between 0 and 100 means that we have some matching characters
            #translate the non matching symbols in alpha
            ctrans = False

            alpha_ct=[]
            for sym in symbol2:
                if isinstance(sym, str):
                    #str in align, means a match
                    alpha_ct.append(sym)
                elif isinstance(sym, list):
                    #list indicates a align of two diff char or symb
                    if sym[0] != '':
                        if isinstance(sym[0],str):
                            ctrans = True
                            alpha_ct.append( FIX_SYMB( self.translate(sym[0]), 1) )
                        else:
                            alpha_ct.append( sym[0] )

            # for i in range(0, len(align1)):
            #     if len(symbol2[i])==1:
            #         alpha_ct.append(align1[i])
            #     else:
            #         if symbol2[i][0] != '':
            #             if isinstance(symbol2[i][0],str):
            #                 ctrans = True
            #                 alpha_ct.append( FIX_SYMB(self.translate(symbol2[i][0]),1) )
            #             else:
            #                 alpha_ct.append(symbol2[i][0])
            if ctrans:
                score_matrix = {
                    'match': self.m,
                    'csetmatch': self.m, # score cset match as full match, since we translated none matching characters to symbol
                    'optional_match': self.om,
                    'mismatch': self.mm,
                    'gapopen': self.go,
                    'gapextend': self.ge
                }
                aligns = align_global(alpha_ct, beta_list,self.translate,  **score_matrix)
                identity, score, align1, symbol2, align2 = finalize(*aligns[0], translate=self.translate)

                self.data['partl1'] = {
                    'score': score, 'identity': identity,
                    'align1': align1, 'align2': align2,
                    'symbol': symbol2
                }
        elif identity == 0:
            #no matching characters:
            alpha_ct = []
            ctrans = False
            for sym in alpha_list:
                if isinstance(sym, str):
                    ctrans = True
                    alpha_ct.append( FIX_SYMB( self.translate(sym), 1) )
                else:
                    alpha_ct.append( sym )
            if ctrans:
                score_matrix = {
                    'match': self.m,
                    'csetmatch': self.m, # uc match counts full
                    'optional_match': self.om,
                    'mismatch': self.mm,
                    'gapopen': self.go,
                    'gapextend': self.ge
                }

                aligns = align_global(alpha_ct, beta_list, self.translate,**score_matrix)
                identity, score, align1, symbol2, align2 = finalize(*aligns[0], translate=self.translate)

                self.data['l1'] = {
                    'score': score, 'identity': identity,
                    'align1': align1, 'align2': align2,
                    'symbol': symbol2
                }



        if len(self.data) > 1:
            def compare(item1, item2):
                #identity before score
                res = item1[1]['identity'] - item2[1]['identity']
                if res == 0:
                    res = item1[1]['score'] - item2[1]['score']
                return res

            _s_al = sorted(enumerate(list(self.data.values())), key=functools.cmp_to_key(compare))
            self.data['best'] = _s_al[-1][1]
        else:
            self.data['best'] = self.data['raw']

    def __repr__(self):
        s = "--ALIGNMENT: {} - {} --".format(repr(self.alpha), repr(self.beta))
        s += "\n costs: m:{} mm:{} go:{} ge:{}".format(self.m,self.mm,self.go,self.ge)
        for key, v in self.data.items():
            identity, score, align1, symbol, align2= v['identity'],v['score'],v['align1'],v['symbol'],v['align2']
            s+="\n {}\n{}".format(key,format_alignment2(identity, score, align1, symbol, align2, indent=2, translate=self.translate))
        return s

    def __str__(self):
        s="--ALIGNMENT({},{},{},{}): {} - {} --".format(self.m,self.mm,self.go,self.ge,self.alpha, self.beta)
        for key, v in self.data.items():
            identity, score, align1, symbol, align2= v['identity'],v['score'],v['align1'],v['symbol'],v['align2']
            s+=" \n[{:^8}] ident: {:6.2f} score: {:>3} SYM: {}".format(key, identity, score, symbol)

        return s


def compare(item1, item2):
    """
    compares first identity and if equals the score
    :param item1:
    :param item2:
    :return:
    """
    data1, data2 = item1[1], item2[1]
    if data1 is None and data2 is None:
        return 0
    elif data1 is None and data2 is not None:
        return -1
    elif data1 is not None and data2 is None:
        return +1
    else:
        res = data1.data['best']['identity'] - data2.data['best']['identity']
        if res == 0:
            res = data1.data['best']['score'] - data2.data['best']['score']
        return res
