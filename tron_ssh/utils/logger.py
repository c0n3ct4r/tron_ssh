
#from consolemenu.format.menu_color import RED, GREEN, YELLOW, DEFAULT

import logging
from logging import Formatter, getLogger, StreamHandler

class Color(object):
    """
     utility to return ansi colored text.
    """

    colors = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
        'bgred': 41,
        'bggrey': 100
    }

    prefix = '\033[1;'

    suffix = '\033[0m'

    def colored(self, text, color=None):
        if color not in self.colors:
            color = 'white'

        clr = self.colors[color]
        return (self.prefix+'%dm%s'+self.suffix) % (clr, text)

colored = Color().colored

class ColoredFormatter(Formatter):
    def format(self, record):
        message = record.getMessage()
        mapping = {
            'INFO': 'cyan',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bgred',
            'DEBUG': 'white',
            'SUCCESS': 'green'
        }
        clr = mapping.get(record.levelname, 'white')
        return colored('%s - %s - %s' % (self.formatTime(record, '%H:%M:%S'), record.levelname, message), clr)

logger = logging.getLogger(__name__)
handler = StreamHandler()
formatter = ColoredFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# set success level
logging.SUCCESS = 25  # between WARNING and INFO
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
setattr(logger, 'success', lambda message, *args: logger._log(logging.SUCCESS, message, args))
logger.setLevel(logging.DEBUG)
