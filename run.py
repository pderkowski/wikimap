#!/usr/bin/env python

import os
import sys
import logging
from wikimap import Utils
from wikimap.BuildManager import BuildManager
from wikimap import Build
import argparse

def main():
    Utils.configLogging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', dest='listSteps', action='store_true',
        help="print a list of steps included in a build")
    parser.add_argument('--noskip', nargs='?', dest='noskip', type=int,
        help="specify which build steps should not be skipped even if otherwise they would be")
    args = parser.parse_args()

    build = Build.Build()

    if args.noskip is not None:
        build[args.noskip].noskip = True

    if args.listSteps:
        for i, s in enumerate(build):
            print '{:2}:\t{}'.format(i, s.name)
    elif "BUILDPATH" not in os.environ:
        logger.critical("Set the BUILDPATH environment variable to the directory where the program will place the generated files.")
        sys.exit(1)
    else:
        manager = BuildManager(os.environ["BUILDPATH"])
        build.setBasePath(manager.newBuild)
        manager.run(build)

if __name__ == "__main__":
    main()
