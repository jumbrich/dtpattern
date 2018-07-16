import datetime
import string
import sys
import unicodedata


_map={}
for i in range(sys.maxunicode):

    ch = chr(i)
    c1,c2 = unicodedata.category(ch)[0],unicodedata.category(ch)
    _map.setdefault(c2, []).append(str(ch))

filename="../src/dtpattern/unicode_categories.py"
fout = open(filename,"w")

import json
fout.write("#created at {}\n\n".format(datetime.datetime.now()))


for k, v in _map.items():
    line = "{} = '{}' \n".format(k,k)
    fout.write(line)

    print("{} = '{}'".format(k, k))

line ="CAT = {}".format(json.dumps(_map))
fout.write(line)



fout.close()
