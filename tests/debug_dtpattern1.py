from csvmimesis.table_generator import create_data_provider_list


from dtpattern.dtpattern1 import pattern
from dtpattern.utils import all_table_unicode

from tests import print_columns

#print(len(all_table_unicode))


import sys

print (sys.getsizeof(1))
print (sys.getsizeof(11))
print (sys.getsizeof("1"))





def pattern1(provider, size, local, seed):
    try:
        header, data=create_data_provider_list(providers=[[provider,1]],  size=size, local=local, seed=seed)

        data=data[header[0]]
        data=[str(d) for d in data]

        p=pattern(data, trans_table=all_table_unicode)

        print("#- {} - {}".format(provider, local))

        print_columns(data, 6)
        print("#=> {}".format(p[0]))
    except Exception as e:
        print("#- {} - {}".format(provider, local))
        print("#=> {} {}".format(type(e).__name__, e))
        raise e


size=10
seed="asdf"
local="de"
provider="address.address"

#pattern1(provider=provider, size=size, seed=seed, local=local)

