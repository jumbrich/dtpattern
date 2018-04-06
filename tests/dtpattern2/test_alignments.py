from contexttimer import Timer

import tests.value_lists as value_lists
from dtpattern.dtpattern2 import Pattern, Alignment
from tests.dtpattern2.inputvalue_generator import *

data=[
    ['http://deri.org/', 'https://deri.com']
]

data_list=[
    [['1'],['1','0','1'],['1','1']]
]

for d in data:
    data_list+=[ [i for i in x] for x in d  ]

#print(data_list)


value_lists.same_length_numbers
value_lists.same_length_lowercase
value_lists.same_length_uppercase


data_pairs=[
    ['123','123'],
    random_time(2)
]

data_lists=[
    ['1','333','12'],
    random_time(10),
    random_iso8601(10),
    random_date(10),
    random_number(3,digits=3, fix_len=True),
    random_isbn10(10),
    random_isbn13(10),
    random_word(100)
]

def test_pairs(data=data_pairs,printRepr=False):

    for d in data:
        print("\n#{:-^60}\n#1: {}\n#2: {}".format('',d[0],d[1]))
        alpha = Pattern(d[0])
        beta  = Pattern(d[1])

        alignment = Alignment(alpha, beta)
        print(alignment)
        if printRepr:
            print(repr(alignment))

def test_pairs_trans(data=data_pairs,printRepr=False):

    for d in data:
        print("\n#{:-^60}\n#1: {}\n#2: {}".format('',d[0],d[1]))
        alpha = Pattern(d[0])
        beta  = Pattern(d[1])

        alignment = Alignment(alpha, beta)
        print(alignment)
        if printRepr:
            print(repr(alignment))

        alpha.update_with_alignment(alignment)
        print(alpha)

        alpha = Pattern(d[1])
        beta = Pattern(d[0])

        alignment = Alignment(alpha, beta)
        print(alignment)
        if printRepr:
            print(repr(alignment))

        alpha.update_with_alignment(alignment)
        print(alpha)


def test_lists(data=data_list, printRepr=False):
    for d in data:
        with Timer(factor=1000) as t:
            print("\n{:#^30}\n>> {} <<".format(' TEST ',d))
            if len(d)<2:
                print("NEED AT LEAST 2 elements")
                return

            alpha = Pattern(d[0])
            for beta in d[1:]:
                beta = Pattern(beta)

                alignment = Alignment(alpha, beta)
                if printRepr:
                    print(repr(alignment))
                alpha.update_with_alignment(alignment)


            print("\n{:-^30}\n>> {}\nDETAILS{}".format(" RESULT ", alpha, repr(alpha)))
            print(alpha._compact())
        print("{:4.3f} ms elapsed for {} values".format(t.elapsed, len(d)))

test_pairs_trans()
#test_lists(data=data_lists,printRepr=False)




