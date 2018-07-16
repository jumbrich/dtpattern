#created at 2018-07-04 15:33:10.216022
import sys
import unicodedata



class Category(object):

    def __init__(self, name, value, desc, parent=None):
        self.name = name
        self.value = value
        self._parent = parent
        self.desc=desc
        self._children = {}
        if parent is not None:
            parent._add_child(self)

    def _add_child(self, child):
        self._children[child.name] = child


    def __repr__(self):
        return "{}({}) '{}'".format(self.name, self.value, self.desc)

    def __str__(self):
        return "{}({}) '{}'".format(self.name, self.value, self.desc)

    def print(self, level =0, ex=None):
        s="{space}{s}".format(space=" " *2* level, s=str(self))
        if ex and self.name in ex:
            s+=" sample={}".format(ex[self.name][:10])
        print(s)
        for child, _child in self._children.items():
            _child.print(level + 1, ex=ex)

    def get_categories(self,level=None):
        if level is None or level<0:
            level = 100
        c=[]

        for child, _child in self._children.items():
            c.append(_child)
            if level and level>0:
                c+=_child.get_categories(level=level-1)
        return c

    def get_only_childs(self):
        c = []
        if len(self._children)==0:
            c.append(self)
        else:
            for child, _child in self._children.items():
                c+=_child.get_only_childs()
        return c

    def get_categories_in_level(self,level=None):
        if level is None or level<0:
            level = 100
        c=[]
        for child, _child in self._children.items():
            if level ==0:
                c.append(_child)
            if level and level>0:
                c+=_child.get_categories(level=level-1)
        return c

    def __hash__(self):
        return hash(repr(self))


"""
Abbr	Long	Description
Lu	Uppercase_Letter	an uppercase letter
Ll	Lowercase_Letter	a lowercase letter
Lt	Titlecase_Letter	a digraphic character, with first part uppercase
LC	Cased_Letter	Lu | Ll | Lt
Lm	Modifier_Letter	a modifier letter
Lo	Other_Letter	other letters, including syllables and ideographs
L	Letter	Lu | Ll | Lt | Lm | Lo
Mn	Nonspacing_Mark	a nonspacing combining mark (zero advance width)
Mc	Spacing_Mark	a spacing combining mark (positive advance width)
Me	Enclosing_Mark	an enclosing combining mark
M	Mark	Mn | Mc | Me
Nd	Decimal_Number	a decimal digit
Nl	Letter_Number	a letterlike numeric character
No	Other_Number	a numeric character of other type
N	Number	Nd | Nl | No
Pc	Connector_Punctuation	a connecting punctuation mark, like a tie
Pd	Dash_Punctuation	a dash or hyphen punctuation mark
Ps	Open_Punctuation	an opening punctuation mark (of a pair)
Pe	Close_Punctuation	a closing punctuation mark (of a pair)
Pi	Initial_Punctuation	an initial quotation mark
Pf	Final_Punctuation	a final quotation mark
Po	Other_Punctuation	a punctuation mark of other type
P	Punctuation	Pc | Pd | Ps | Pe | Pi | Pf | Po
Sm	Math_Symbol	a symbol of mathematical use
Sc	Currency_Symbol	a currency sign
Sk	Modifier_Symbol	a non-letterlike modifier symbol
So	Other_Symbol	a symbol of other type
S	Symbol	Sm | Sc | Sk | So
Zs	Space_Separator	a space character (of various non-zero widths)
Zl	Line_Separator	U+2028 LINE SEPARATOR only
Zp	Paragraph_Separator	U+2029 PARAGRAPH SEPARATOR only
Z	Separator	Zs | Zl | Zp
Cc	Control	a C0 or C1 control code
Cf	Format	a format control character
Cs	Surrogate	a surrogate code point
Co	Private_Use	a private-use character
Cn	Unassigned	a reserved unassigned code point or a noncharacter
C	Other	Cc | Cf | Cs | Co | Cn

"""

ALL=0




A = Category('A', ALL, 'L | M | N | P | Z | C | S')

#just a container to store all UCs
_all=[]

Letter=1
Cased_Letter= 11
Uppercase_Letter=112
Lowercase_Letter=113
Titlecase_Letter=114
Modifier_Letter=12
Other_Letter=13

L = Category('L',Letter, 'Lu | Ll | Lt | Lm | Lo',A)
LC = Category('LC',	Cased_Letter,	'Lu | Ll | Lt',L)
Lu = Category('Lu',	Uppercase_Letter, 'an uppercase letter', LC)
Ll = Category('Ll',	Lowercase_Letter,	'a lowercase letter',LC)
Lt = Category('Lt',	Titlecase_Letter,	'a digraphic character, with first part uppercase',LC)
Lm = Category('Lm',	Modifier_Letter,	'a modifier letter',L)
Lo = Category('Lo',	Other_Letter,	'other letters, including syllables and ideographs',L)

_ls=[Lu,Ll,Lt,Lm,Lo]
_all+=_ls

Mark=2
Nonspacing_Mark=21
Spacing_Mark=22
Enclosing_Mark=23
M = Category('M',Mark, 'Mn | Mc | Me',A)

Mn = Category('Mn',Nonspacing_Mark, 'a nonspacing combining mark (zero advance width)',M)
Mc = Category('Mc',Spacing_Mark, 'a spacing combining mark (positive advance width)',M)
Me = Category('Me',Enclosing_Mark, 'an enclosing combining mark',M)

_ms=[Mn,Mc,Me]
_all+=_ms

Number=3
Decimal_Number=31
Letter_Number=32
Other_Number=33
N = Category('N',Number, 'Nd | Nl | No',A)

Nd = Category('Nd',Decimal_Number, 'a decimal digit',N)
Nl = Category('Nl',Letter_Number, 'a letterlike numeric character',N)
No = Category('No',Other_Number, 'a numeric character of other type',N)

_ns=[Nd,Nl,No]
_all += _ns

Punctuation=4
Connector_Punctuation=41
Dash_Punctuation=42
Open_Punctuation=43
Close_Punctuation=44
Initial_Punctuation=45
Final_Punctuation=46
Other_Punctuation=47
P = Category('P',	Punctuation ,"Pc | Pd | Ps | Pe | Pi | Pf | Po)",A)
Pc = Category('Pc',	Connector_Punctuation ,"a connecting punctuation mark, like a tie", P)
Pd = Category('Pd',	Dash_Punctuation ,"a dash or hyphen punctuation mark", P)
Ps = Category('Ps',	Open_Punctuation ,"an opening punctuation mark (of a pair)", P)
Pe = Category('Pe',	Close_Punctuation ,"a closing punctuation mark (of a pair)", P)
Pi = Category('Pi',	Initial_Punctuation ,"an initial quotation mark", P)
Pf = Category('Pf',	Final_Punctuation ,"a final quotation mark", P)
Po = Category('Po',	Other_Punctuation ,"a punctuation mark of other type", P)
_ps=[ Pc,Pd,Ps,Pe,Pi,Pf,Po]
_all += _ps


Symbol=5
Math_Symbol=51
Currency_Symbol=52
Modifier_Symbol=53
Other_Symbol=54
S = Category('S',	Symbol	,"Sm | Sc | Sk | So",A)
Sm = Category('Sm',	Math_Symbol	,"a symbol of mathematical use",S)
Sc = Category('Sc',	Currency_Symbol	,"a currency sign",S)
Sk = Category('Sk',	Modifier_Symbol	,"a non-letterlike modifier symbol",S)
So = Category('So',	Other_Symbol	,"a symbol of other type",S)

_ss=[ Sm,Sc, Sk, So]
_all += _ss

Separator=6
Space_Separator=61
Line_Separator=62
Paragraph_Separator=63
Z = Category('Z',	Separator	,"Zs | Zl | Zp",A)
Zs = Category('Zs',	Space_Separator	,"a space character (of various non-zero widths)",Z)
Zl = Category('Zl',	Line_Separator	,"U+2028 LINE SEPARATOR only",Z)
Zp = Category('Zp',	Paragraph_Separator	,"U+2029 PARAGRAPH SEPARATOR only",Z)

_zs=[ Zs, Zl, Zp]
_all += _zs

Other=7
Control=71
Format=72
Surrogate=73
Private_Use=74
Unassigned = 75
C = Category('C',	Other	,"Cc | Cf | Cs | Co | Cn",A)
Cc = Category('Cc',	Control	,"a C0 or C1 control code",C)
Cf = Category('Cf',	Format	,"a format control character",C)
Cs = Category('Cs',	Surrogate	,"a surrogate code point",C)
Co = Category('Co',	Private_Use	,"a private-use character",C)
Cn = Category('Cn',	Unassigned	,"a reserved unassigned code point or a noncharacter",C)

_cs=[ Cc,Cf, Cs, Co, Cn]
_all += _cs


##SOME EXTRA used in higher-level

WORD = S = Category('W', 8	,"Lu Ll")

CAT={}
for i in range(sys.maxunicode):
    ch = chr(i)
    c1,c2 = unicodedata.category(ch)[0],unicodedata.category(ch)
    CAT.setdefault(c2, []).append(str(ch))




def aggregate_CAT(CAT, cats):
    d={}
    for c in cats:
        dd=d.setdefault(c.name,[])
        for _c in c.get_only_childs():
            dd+=CAT[_c.name]
    return d

def aggregate_table(cats):
    d = {}
    for c in cats:
        for _c in c.get_categories():
            d[_c.value]= c.value
        d[c.value] = c.value

    return d
#A.get_only_childs()

#print(sorted(CAT.keys()))
#c=aggregate_CAT(CAT, A.get_categories_in_level(level=0))
#print(c.keys())
#cc=A.get_categories_in_level(level=1)
#print(len(cc))
#for c in cc:
#    c.print()
#   print( [c.name for c in c.get_only_childs()])

