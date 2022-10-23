import logging
import urllib
import tarfile
import tempfile
from time import time
import LogUtils

def download(url, output_path):
    urllib.urlretrieve(url, output_path, reporthook=LogUtils.ProgressBar(url).report)

def download_and_extract(url, output_path):
    logger = logging.getLogger(__name__)

    with tempfile.NamedTemporaryFile() as temp:
        urllib.urlretrieve(url, temp.name, reporthook=LogUtils.ProgressBar(url).report)
        logger.info('Extracting to {}...'.format(output_path))
        with tarfile.open(temp.name) as tar:
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, output_path)

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
