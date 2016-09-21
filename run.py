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
    parser.add_argument('--noskip', nargs='?', dest='noskip', type=int, default=-1,
        help="specify which build steps should not be skipped even if otherwise they would be")
    args = parser.parse_args()

    build = Build.build()

    if args.noskip is not None:
        if args.noskip == -1:
            noskip = range(len(build))
        else:
            noskip = [args.noskip]

        for j in noskip:
            build[j].noskip = True

    if args.listSteps:
        for i, s in enumerate(build):
            print '{:2}:\t{}'.format(i, s.name)
    elif "BUILDPATH" not in os.environ:
        logger.critical("Set the BUILDPATH environment variable to a directory where you want the program to place the results in.")
        sys.exit(1)
    else:
        manager = BuildManager(os.environ["BUILDPATH"])
        manager.run(build, {})

if __name__=="__main__":
    main()