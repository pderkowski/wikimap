import logging
import sys
import urllib
import tarfile
import tempfile
from time import time
import ast
import pprint

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

class Bunch(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class SimpleTimer(object):
    def __init__(self):
        self._start = time()

    def __call__(self):
        return time() - self._start

def load_dict(path):
    with open(path, 'r') as f:
        return ast.literal_eval(f.read()) # literal_eval only evaluates basic types instead of arbitrary code

def save_dict(path, dict_):
    with open(path, 'w') as f:
        pprint.pprint(dict_, f)
