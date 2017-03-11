from time import time
import os
import errno
import shutil
import ast

class SimpleTimer(object):
    def __init__(self):
        self._start = time()

    def __call__(self):
        return time() - self._start

def format_duration(secs):
    hours, rem = divmod(secs, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:06.3f}".format(int(hours), int(minutes), seconds)

def make_links(path_pairs):
    for src, dst in path_pairs:
        make_link(src, dst)

def make_link(src, dst):
    try:
        link_directory(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            if not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            if not os.path.exists(dst):
                os.link(src, dst)
        else: raise

def link_directory(src, dst):
    names = os.listdir(src)
    os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                link_directory(srcname, dstname)
            else:
                os.link(srcname, dstname)
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

def get_subdirs(directory):
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

def load_dict(path):
    with open(path, 'r') as f:
        return ast.literal_eval(f.read()) # literal_eval only evaluates basic types instead of arbitrary code

def save_dict(path, dict_):
    with open(path, 'w') as f:
        f.write(str(dict_))
