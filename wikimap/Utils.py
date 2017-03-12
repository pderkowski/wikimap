import logging
import sys
import os
import shutil
import urllib
import numpy
import tarfile
import tempfile
from prettytable import PrettyTable

class SingleProcessFilter(logging.Filter):
    master_pid = None

    def filter(self, record):
        pid = os.getpid()
        return self.master_pid != None and pid == self.master_pid

def config_logging():
    logging.basicConfig(format='\33[2K\r%(asctime)s:%(filename)s:%(lineno)d:%(message)s', datefmt='%H:%M:%S', level=logging.INFO)
    SingleProcessFilter.master_pid = os.getpid()

def get_logger(name):
    logger = logging.getLogger(name)
    logger.addFilter(SingleProcessFilter())
    return logger

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

def download(url, output_path):
    urllib.urlretrieve(url, output_path, reporthook=ProgressBar(url).report)

def download_and_extract(url, output_path):
    logger = logging.getLogger(__name__)

    with tempfile.NamedTemporaryFile() as temp:
        urllib.urlretrieve(url, temp.name, reporthook=ProgressBar(url).report)
        logger.info('Extracting to {}...'.format(output_path))
        with tarfile.open(temp.name) as tar:
            tar.extractall(output_path)

def any2unicode(sth, encoding='utf8', errors='strict'):
    if isinstance(sth, unicode):
        return sth
    elif isinstance(sth, basestring):
        return unicode(sth, encoding, errors=errors)
    else:
        return unicode(str(sth), encoding, errors=errors)

def any2array(something):
    if isinstance(something, numpy.ndarray):
        return something
    elif isinstance(something, list):
        return numpy.array(something)
    elif hasattr(something, "__iter__"):
        return numpy.array(list(something))
    else:
        raise ValueError("Argument is not convertable to an array.")

def clear_directory(directory):
    for f in os.listdir(directory):
        file_path = os.path.join(directory, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print e

def make_table(headers, alignement, rows):
    table = PrettyTable(headers)
    for i, h in enumerate(headers):
        table.align[h] = alignement[i]
    for r in rows:
        table.add_row(r)
    return table

class Colors(object):
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'

def color_text(string, color):
    return color + string + '\033[0m'

def pack(files, dest_dir, dest_name):
    logger = logging.getLogger(__name__)
    with tarfile.open(os.path.join(dest_dir, dest_name), "w:gz") as tar:
        for f in files:
            logger.info('Adding {} to archive.'.format(f))
            tar.add(f, arcname=os.path.basename(f))
