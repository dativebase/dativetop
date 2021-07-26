import logging
from logging.config import dictConfig
import os


from dativetop.constants import HERE


logging_config = dict(
    version=1,
    formatters={
        'f': {'format':
              '%(asctime)s %(name)-32s %(levelname)-8s %(message)s'}
    },
    handlers={
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
            'level': logging.INFO
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(HERE, 'dativetop.log'),
            'mode': 'a',
            'formatter': 'f'
        },
    },
    root={
        'handlers': ['file'],
        'level': logging.INFO,
    },
)

dictConfig(logging_config)

logger = logging.getLogger(__name__)
