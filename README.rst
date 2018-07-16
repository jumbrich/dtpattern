=========
dtpattern
=========


A library to detect abstract patterns over a list of values


Description
===========

This library tries to summaries a list of values using an abstract pattern language.

In a nutshell, the algorithm works like this.

1) Try to find shared character sequences using a SuffixTree
2) split patterns into shared sequences and non-shared sequences
3) try to aggregate non-shared sequences

We start by parsign the strings in their original format and detect shared character sequences.
next, we map the input characters to their respective unicode categories and perform again a shared pattern sequence approach


Install
=======
1. Using pip install::

   #>pip install dtpattern

2. Using the source from the repository
 This should be straight forward
    a) git checkout
    b) python setup.py install|develop


Pattern representation
======================

We represent a pattern based on the unicode categories (UCs).
For a list of used unicode categories just run::

    #> dtpattern ucs
        A(0) 'L | M | N | P | Z | C | S'
          L(1) 'Lu | Ll | Lt | Lm | Lo'
            LC(11) 'Lu | Ll | Lt'
              Lu(112) 'an uppercase letter' sample=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
              Ll(113) 'a lowercase letter' sample=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
              Lt(114) 'a digraphic character, with first part uppercase' sample=['ǅ', 'ǈ', 'ǋ', 'ǲ', 'ᾈ', 'ᾉ', 'ᾊ', 'ᾋ', 'ᾌ', 'ᾍ']
            Lm(12) 'a modifier letter' sample=['ʰ', 'ʱ', 'ʲ', 'ʳ', 'ʴ', 'ʵ', 'ʶ', 'ʷ', 'ʸ', 'ʹ']
            Lo(13) 'other letters, including syllables and ideographs' sample=['ª', 'º', 'ƻ', 'ǀ', 'ǁ', 'ǂ', 'ǃ', 'ʔ', 'א', 'ב']
          M(2) 'Mn | Mc | Me'
            Mn(21) 'a nonspacing combining mark (zero advance width)' sample=['̀', '́', '̂', '̃', '̄', '̅', '̆', '̇', '̈', '̉']
            Mc(22) 'a spacing combining mark (positive advance width)' sample=['ः', 'ऻ', 'ा', 'ि', 'ी', 'ॉ', 'ॊ', 'ो', 'ौ', 'ॎ']
            Me(23) 'an enclosing combining mark' sample=['҈', '҉', '᪾', '⃝', '⃞', '⃟', '⃠', '⃢', '⃣', '⃤']
          N(3) 'Nd | Nl | No'
            Nd(31) 'a decimal digit' sample=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            Nl(32) 'a letterlike numeric character' sample=['ᛮ', 'ᛯ', 'ᛰ', 'Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ']
            No(33) 'a numeric character of other type' sample=['²', '³', '¹', '¼', '½', '¾', '৴', '৵', '৶', '৷']
          P(4) 'Pc | Pd | Ps | Pe | Pi | Pf | Po)'
            Pc(41) 'a connecting punctuation mark, like a tie' sample=['_', '‿', '⁀', '⁔', '︳', '︴', '﹍', '﹎', '﹏', '＿']
            Pd(42) 'a dash or hyphen punctuation mark' sample=['-', '֊', '־', '᐀', '᠆', '‐', '‑', '‒', '–', '—']
            Ps(43) 'an opening punctuation mark (of a pair)' sample=['(', '[', '{', '༺', '༼', '᚛', '‚', '„', '⁅', '⁽']
            Pe(44) 'a closing punctuation mark (of a pair)' sample=[')', ']', '}', '༻', '༽', '᚜', '⁆', '⁾', '₎', '⌉']
            Pi(45) 'an initial quotation mark' sample=['«', '‘', '‛', '“', '‟', '‹', '⸂', '⸄', '⸉', '⸌']
            Pf(46) 'a final quotation mark' sample=['»', '’', '”', '›', '⸃', '⸅', '⸊', '⸍', '⸝', '⸡']
            Po(47) 'a punctuation mark of other type' sample=['!', '"', '#', '%', '&', "'", '*', ',', '.', '/']
          S(5) 'Sm | Sc | Sk | So'
            Sm(51) 'a symbol of mathematical use' sample=['+', '<', '=', '>', '|', '~', '¬', '±', '×', '÷']
            Sc(52) 'a currency sign' sample=['$', '¢', '£', '¤', '¥', '֏', '؋', '৲', '৳', '৻']
            Sk(53) 'a non-letterlike modifier symbol' sample=['^', '`', '¨', '¯', '´', '¸', '˂', '˃', '˄', '˅']
            So(54) 'a symbol of other type' sample=['¦', '©', '®', '°', '҂', '֍', '֎', '؎', '؏', '۞']
          Z(6) 'Zs | Zl | Zp'
            Zs(61) 'a space character (of various non-zero widths)' sample=[' ', '\xa0', '\u1680', '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006']
            Zl(62) 'U+2028 LINE SEPARATOR only' sample=['\u2028']
            Zp(63) 'U+2029 PARAGRAPH SEPARATOR only' sample=['\u2029']
          C(7) 'Cc | Cf | Cs | Co | Cn'
            Cc(71) 'a C0 or C1 control code' sample=['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\t']
            Cf(72) 'a format control character' sample=['\xad', '\u0600', '\u0601', '\u0602', '\u0603', '\u0604', '\u0605', '\u061c', '\u06dd', '\u070f']
            Cs(73) 'a surrogate code point' sample=['\ud800', '\ud801', '\ud802', '\ud803', '\ud804', '\ud805', '\ud806', '\ud807', '\ud808', '\ud809']
            Co(74) 'a private-use character' sample=['\ue000', '\ue001', '\ue002', '\ue003', '\ue004', '\ue005', '\ue006', '\ue007', '\ue008', '\ue009']
            Cn(75) 'a reserved unassigned code point or a noncharacter' sample=['\u0378', '\u0379', '\u0380', '\u0381', '\u0382', '\u0383', '\u038b', '\u038d', '\u03a2', '\u0530']

In addition, we try to summaries UCs based on their hierachy.

**possible representations**
+----------+---------------------------------------------------------+
| Pattern Example | Meaning                                          |
+==========+=========================================================+
| Lu       | One upper case character           |
+----------+---------------------------------------------------------+
| Lu** | LuLuLu | Lu3    | Three upper case character           |
+----------+---------------------------------------------------------+
| Lu?? | Lu{1,3}     | One to three upper case character           |
+----------+---------------------------------------------------------+
| Lu**?? | Lu{3,5     | Three to five upper case character           |
+----------+---------------------------------------------------------+
| (Lu3)#3     | Three values have an optional Lu3 pattern           |
+----------+---------------------------------------------------------+
| [Lu,Po]{1,4}     |  There are one to four characters which are either Lu or Po           |
+----------+---------------------------------------------------------+


Examples
========

a) *Address zip codes*::

    #>dtpattern demo -p address -m zip_code

    datagenerator(local=en, size=10, provider=address, method=zip_code)

    -- en-address.zip_code
     --------------------------------------------- DATA ----------------------------------------------
     |33797|80214|70736|89278|07142|77897|47476|69332|45411|31792|
     -------------------------------------------------------------------------------------------------
      RESULT_PATTERN(pattern=[FIX_SYMB(symbol=31, len=5)], count=10)
      CALL: pattern_to_string(pat, collapse_level=0)
       >> NdNdNdNdNd
      CALL: pattern_to_string(pat, collapse_level=1)
       >> Nd****
      CALL: pattern_to_string(pat, collapse_level=2)
       >> Nd5
      CALL: pattern_to_string( higher_level(pat), collapse_level=2)
         PAT(pattern=[FIX_SYMB(symbol=31, len=5)], count=10)
       >> Nd5

We can see that all input values consist of exactly 5 digits, as such the final pattern **Nd5**


b) *datetime date*::

    dtpattern demo -p datetime -m date

    datagenerator(local=en, size=10, provider=datetime, method=date)

    -- en-datetime.date
     ----------------------------------------- DATA ------------------------------------------
     |12/12/2022|09/30/2026|01/04/2011|04/20/2017|12/16/2008|12/05/2005|11/26/2003|11/21/2023|
     |12/10/2003|05/27/2003|
     -----------------------------------------------------------------------------------------
      RESULT_PATTERN(pattern=[FIX_SYMB(symbol=31, len=2), FIX_SYMB(symbol=47, len=1), FIX_SYMB(symbol=31, len=2), FIX_SYMB(symbol=47, len=1), FIX_SYMB(symbol=31, len=4)], count=10)
      CALL: pattern_to_string(pat, collapse_level=0)
       >> NdNd Po NdNd Po NdNdNdNd
      CALL: pattern_to_string(pat, collapse_level=1)
       >> Nd* Po Nd* Po Nd***
      CALL: pattern_to_string(pat, collapse_level=2)
       >> Nd2 Po Nd2 Po Nd4
      CALL: pattern_to_string( higher_level(pat), collapse_level=2)
         PAT(pattern=[FIX_SYMB(symbol=31, len=2), FIX_SYMB(symbol=47, len=1), FIX_SYMB(symbol=31, len=2), FIX_SYMB(symbol=47, len=1), FIX_SYMB(symbol=31, len=4)], count=10)
       >> Nd2 Po Nd2 Po Nd4

This example has as input date values and the final pattern is **Nd2 Po Nd2 Po Nd4** (*two digits (Nd2), a whitespace (Po), two digits (Nd2), another whitespace (Po) and four more digits (Nd4)

Note
====

The documentation is currently very vague and requires further work.
We try to cleanup and document our algorithm.

This project has been set up using PyScaffold 3.0.3. For details and usage
information on PyScaffold see http://pyscaffold.org/.
