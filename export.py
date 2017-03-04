#!/usr/bin/env python

from wikimap.BuildManager import BuildManager
from wikimap.Paths import *
from wikimap import Utils
from wikimap import Paths
import argparse
import logging
import os
import sys
import tarfile

filesets = {
    'ui'    : [wikimap_points, wikimap_categories, zoom_index, metadata, aggregated_inlinks, aggregated_outlinks]
}

def pack(files, destDir):
    logger = logging.getLogger(__name__)

    with tarfile.open(os.path.join(destDir, "build.tar.gz"), "w:gz") as tar:
        for f in files:
            logger.info('Adding {} to archive.'.format(f))
            tar.add(f, arcname=os.path.basename(f))

def export(files, destDir):
    destDir = os.path.realpath(destDir)

    logger = logging.getLogger(__name__)
    logger.info('EXPORTING RESULTS TO {}'.format(destDir))

    if not os.path.isdir(destDir):
        print 'Destdir: ', destDir
        os.makedirs(destDir)

    Utils.clearDirectory(destDir)
    pack(files, destDir)

def main():
    Utils.configLogging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('fileset', help="specify the fileset to be exported", choices=['ui', 'plots'])
    args = parser.parse_args()

    if "BUILDPATH" not in os.environ:
        logger.critical("Set the BUILDPATH environment variable.")
        sys.exit(1)

    if "EXPORTPATH" not in os.environ:
        logger.critical("Set the EXPORTPATH environment variable.")
        sys.exit(1)

    manager = BuildManager(os.environ["BUILDPATH"])
    Paths.global_base = manager.lastBuild

    export(Paths.resolve(filesets[args.fileset]), os.environ["EXPORTPATH"])

if __name__ == '__main__':
    main()
