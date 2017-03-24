import shutil
import os
import logging
import tarfile
import errno

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

def pack(files, dest_dir, dest_name):
    logger = logging.getLogger(__name__)
    with tarfile.open(os.path.join(dest_dir, dest_name), "w:gz") as tar:
        for f in files:
            logger.info('Adding {} to archive.'.format(f))
            tar.add(f, arcname=os.path.basename(f))

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
