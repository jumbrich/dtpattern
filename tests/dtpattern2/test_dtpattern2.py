from contexttimer import Timer

from dtpattern import debugConf, defaultConf, fileConf, infoConf
from dtpattern.dtpattern2 import PatternFinder, compress_strategies

#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)-8s - %(name)s - %(message)s  ')
#logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s - %(message)s')
from tests.dtpattern2.inputvalue_generator import *


import logging
import logging.config
logging.config.dictConfig(debugConf)
logger = logging.getLogger(__name__)


input_values=[str(i) for i in range(1,99)]
input_values=['http://deri.org/','https://deri.com']

data_lists=[
    (['111','222','Wien','Salzburg'],2),
    #(['1','WW','131W','ac123ac','cb-d-','http://'],2),
    #random_time(10),
    #random_iso8601(10),
    #random_date(10),
    #random_number(3,digits=3, fix_len=True),
    #random_isbn10(10),
    #random_isbn13(10),
    #random_word(100)
    #random_number(1000,digits=2, fix_len=False)
]



def get_patterns(d, groups):
    with Timer(factor=1000) as t:
        pm = PatternFinder(max_pattern=groups)
        logger.info("adding {} values (first 10: {} )".format(len(d),d[:10]))
        for value in d:
            logger.debug("->ADD {}".format(value))
            pm.add(value)
            logger.debug("<-ADD after adding value %s %s",value, pm)
            logger.debug(repr(pm))
        logger.info(pm)
        logger.info(repr(pm))
        logger.info(pm.info())

for d,g in data_lists:
    get_patterns(d,g)
