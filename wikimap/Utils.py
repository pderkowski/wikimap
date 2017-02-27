import logging
import sys
import os
import shutil
import errno
import subprocess
import ast
import urllib
import numpy
import tarfile
import tempfile

def openOrExit(file_, mode='r'):
    logger = logging.getLogger(__name__)

    if mode == 'r' and not os.path.isfile(file_):
        logger.error('File {} does not exist.'.format(file_))
        sys.exit()
    else:
        return open(file_, mode)

def getProgName(fileName):
    return os.path.splitext(os.path.basename(fileName))[0]

def formatDuration(secs):
    hours, rem = divmod(secs, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

def configLogging():
    logging.basicConfig(format='\33[2K\r%(asctime)s:%(filename)s:%(lineno)d:%(message)s', datefmt='%H:%M:%S', level=logging.INFO)

def getParentDirectory(file_):
    return os.path.join(os.path.dirname(os.path.abspath(file_)), '..')

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

def call(command):
    logger = logging.getLogger(__name__)
    logger.info('Running command: {}'.format(command))
    subprocess.call(command, shell=True)

def loadFromFile(path):
    with open(path, 'r') as f:
        return ast.literal_eval(f.read()) # literal_eval only evaluates basic types instead of arbitrary code

def saveToFile(path, dict_):
    with open(path, 'w') as f:
        f.write(str(dict_))

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

def linkDirectory(src, dst):
    names = os.listdir(src)
    os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                linkDirectory(srcname, dstname)
            else:
                os.link(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except StandardError as err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # can't copy file access times on Windows
        if why.winerror is None:
            errors.extend((src, dst, str(why)))
    if errors:
        raise StandardError(errors)

def clearDirectory(directory):
    for f in os.listdir(directory):
        file_path = os.path.join(directory, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def copyFiles(files, destDir, verbose=False):
    logger = logging.getLogger(__name__)

    for f in files:
        if os.path.exists(f):
            if verbose:
                logger.info("Copying {}".format(f))

            name = os.path.basename(f)
            dest = os.path.join(destDir, name)

            try:
                shutil.copytree(f, dest)
            except OSError as exc: # python >2.5
                if exc.errno == errno.ENOTDIR:
                    shutil.copyfile(f, dest)
                else: raise

def basename(path):
    return os.path.basename(path)
