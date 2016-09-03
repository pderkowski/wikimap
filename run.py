#!/usr/bin/env python

import os
import sys
import logging
from wikimap import Utils
from wikimap.BuildManager import BuildManager
from wikimap import Build

def main():
    Utils.configLogging()
    logger = logging.getLogger(__name__)

    if "BUILDPATH" not in os.environ:
        logger.critical("Set the BUILDPATH environment variable to a directory where you want the program to place the results in.")
        sys.exit(1)
    else:
        manager = BuildManager(os.environ["BUILDPATH"])
        manager.run(Build.build(), {})

if __name__=="__main__":
    main()