#!/usr/bin/env python

import argparse
import logging
import os
import sys
from wikimap.BuildManager import BuildManager
from wikimap.common.Paths import paths as Path
import wikimap.common.Paths as Paths
import wikimap.Utils as Utils

filesets = {
    'ui': [Path['wikimapPoints'], Path['wikimapCategories'], Path['zoomIndex'], Path['metadata'], Path['termIndex']]
}

def export(files, destDir):
    destDir = os.path.realpath(destDir)

    logger = logging.getLogger(__name__)
    logger.info('EXPORTING RESULTS TO {}'.format(destDir))

    if not os.path.isdir(destDir):
        print 'Destdir: ', destDir
        os.makedirs(destDir)

    Utils.clearDirectory(destDir)
    Utils.copyFiles(files, destDir, verbose=True)

def main():
    Utils.configLogging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('fileset', help="specify the fileset to be exported", choices=['ui'])
    args = parser.parse_args()

    if "BUILDPATH" not in os.environ:
        logger.critical("Set the BUILDPATH environment variable.")
        sys.exit(1)

    if "EXPORTPATH" not in os.environ:
        logger.critical("Set the EXPORTPATH environment variable.")
        sys.exit(1)

    manager = BuildManager(os.environ["BUILDPATH"])
    Path.base = manager.lastBuild

    export(Paths.resolve(filesets[args.fileset]), os.environ["EXPORTPATH"])

if __name__ == '__main__':
    main()
