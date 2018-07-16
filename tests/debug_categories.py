from difflib import SequenceMatcher as SM

from dtpattern.suffix_tree_lists import STree
from dtpattern.unicode_translate.unicode_categories import A,CAT
A.print(ex=CAT)


a=[1,12,3]
b=[0,12,3,4,12,13]
match = SM(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
print(match)

print(a[match.a:match.a+match.size])



st = STree([a,b])
lcs = st.lcs()
print(lcs)
