# -*- coding: utf-8 -*-

"""Top-level package for dtpattern."""


__author__ = """Juergen Umbrich"""
__email__ = 'jueumb@gmail.com'
__version__ = '0.3'


import logging
import logging.config
logging.getLogger(__name__).addHandler(logging.NullHandler())


defaultConf={
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)8s - %(message)s'
        },
        'debug': {
            'format': '[%(asctime)s] %(levelname)8s %(message)s (%(filename)s:%(lineno)s)'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'console_debug': {
            'level': 'DEBUG',
            'formatter': 'debug',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'debug',
            'filename': 'debug.log',
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True
        }
    }
}
import copy

infoConf=copy.deepcopy(defaultConf)
infoConf['loggers']['']['handlers']=['console']
infoConf['loggers']['']['level']='INFO'


debugConf=copy.deepcopy(defaultConf)
debugConf['loggers']['']['handlers']=['console_debug']
debugConf['loggers']['']['level']='DEBUG'


fileConf=copy.deepcopy(defaultConf)
fileConf['loggers']['']['handlers']=['console','file']
debugConf['loggers']['']['level']='DEBUG'

logging.config.dictConfig(defaultConf)
