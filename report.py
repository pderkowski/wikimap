#!/usr/bin/env python

import argparse
import os
import sys
from wikimap import Utils, ReportCreator

def main():
    logger = Utils.get_logger(__name__)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--buildpath', '-b', dest='buildpath', type=str, default=os.environ.get("WIKIMAP_BUILDPATH", None),
        help="Specify a directory where builds are located. Can also be set by WIKIMAP_BUILDPATH environment variable.")
    parser.add_argument('--reportpath', '-r', dest='reportpath', type=str, default=os.environ.get("WIKIMAP_REPORTPATH", None),
        help="Specify a path for the report. Can also be set by WIKIMAP_REPORTPATH environment variable.")
    parser.add_argument('--prefix', '-p', dest='prefix', type=str, default='build',
        help="Specify a prefix of subdirectories inside the builds directory.")
    parser.add_argument('indices', type=Utils.parse_int_range,
        help="Specify the indices of builds to include in the report.")
    args = parser.parse_args()

    if not args.buildpath:
        sys.exit("Specify the build path, using --buildpath (-b) option or by setting the WIKIMAP_BUILDPATH environment variable.")

    if not args.reportpath:
        sys.exit("Specify the report path, using --reportpath (-r) option or by setting the WIKIMAP_REPORTPATH environment variable.")

    try:
        creator = ReportCreator(args.buildpath, args.prefix)
        creator.make_plot(args.indices, args.reportpath)
    except Exception, e:
        logger.exception(e)
        raise

if __name__ == '__main__':
    Utils.config_logging()
    main()
