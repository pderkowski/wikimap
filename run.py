#!/usr/bin/env python

import os
import sys
import logging
from wikimap import Utils
from wikimap.BuildManager import BuildManager
from wikimap import Build
import argparse

def parseNoskip(noskipStr, maxNumber):
    parts = noskipStr.split(',')
    noskipped = []
    for p in parts:
        p = p.strip()
        split = p.find('-')
        if split == -1: # p is like '12'
            noskipped.append(int(p))
        elif split == 0: # p is like '-12'
            noskipped.extend(range(0, int(p[1:]) + 1))
        elif split == len(p) - 1: # p is like '12-'
            noskipped.extend(range(int(p[:-1]), maxNumber + 1))
        else: # p is like '1-12'
            noskipped.extend(range(int(p[:split]), int(p[split+1:]) + 1))
    return noskipped

def main():
    Utils.configLogging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', dest='listSteps', action='store_true',
        help="print a list of steps included in a build")
    parser.add_argument('--noskip', nargs='?', dest='noskip', type=str,
        help="specify which build steps should not be skipped even if otherwise they would be")
    args = parser.parse_args()

    build = Build.Build()

    if args.noskip is not None:
        for n in parseNoskip(args.noskip, len(build.jobs) - 1):
            build[n].noskip = True

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
