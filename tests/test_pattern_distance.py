

A pattern should have

* a strign representation which can be used to parse the pattern
* actual values -> could be a list with None items
* aggregated parts
* high level representation

123
    d
    ddd|d3|3d
    123

http://
    c,://
    4c,://
    http,://

Wien
    C,c
    C,ccc
    W,ien
    "Wien"

Berlin
    C,c
    C,ccccc
    B,erlin
    "Berlin"

Wien, Berlin
    C,c
    C,c{3,5}
http
https


123 123 -> equal, dont do anything

123 124 -> we should detect that 12 is equal and then both numbers

123 45 -> all numbers, but no common substring,
[ddd,C,ccc]
[123,]
