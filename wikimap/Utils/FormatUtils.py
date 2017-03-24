import math
from prettytable import PrettyTable

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
