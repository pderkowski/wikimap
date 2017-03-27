import logging
import os
import sys
import math
from prettytable import PrettyTable

logging.IMPORTANT = 25
logging.addLevelName(logging.IMPORTANT, "IMPORTANT")

thick_line_separator = '='*80
thin_line_separator = '-'*80

def important(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(logging.IMPORTANT):
        self._log(logging.IMPORTANT, message, args, **kws)

logging.Logger.important = important

class SingleProcessFilter(logging.Filter):
    master_pid = None

    def filter(self, record):
        pid = os.getpid()
        return self.master_pid != None and pid == self.master_pid

def config_logging(only_important=False):
    level = logging.IMPORTANT if only_important else logging.INFO
    logging.basicConfig(format='\33[2K\r%(asctime)s:%(filename)s:%(lineno)d:%(message)s', datefmt='%H:%M:%S', level=level)
    SingleProcessFilter.master_pid = os.getpid()

def get_logger(name):
    logger = logging.getLogger(name)
    logger.addFilter(SingleProcessFilter())
    return logger

def format_duration(secs):
    hours, rem = divmod(secs, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:06.3f}".format(int(hours), int(minutes), seconds)

def get_number_width(number):
    return int(math.ceil(math.log10(number + 1)))

def make_table(headers, rows, alignement, **kwargs):
    table = PrettyTable(headers, **kwargs)
    for i, h in enumerate(headers):
        table.align[h] = alignement[i]
    for r in rows:
        table.add_row(r)
    return table.get_string()

class Colors(object):
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'

def color_text(string, color):
    return color + string + '\033[0m'

class ProgressBar(object):
    def __init__(self, name):
        self.name = name

    def report(self, count, blockSize, totalSize):
        percent = int(count*blockSize*100/totalSize)

        if count*blockSize > totalSize:
            sys.stdout.write("\33[2K\r" + self.name + "...DONE\n")
        else:
            sys.stdout.write("\33[2K\r" + self.name + "...%d%%" % percent)
        sys.stdout.flush()
