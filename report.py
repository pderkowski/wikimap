#!/usr/bin/env python

import argparse
import os
import sys
from wikimap import Utils, BuildExplorer
from pprint import pprint

class ReportCreator(object):
    def __init__(self, build_explorer):
        self._build_explorer = build_explorer

    def print_results(self, build_indices):
        results = self._collect_results_from_builds(build_indices)
        pprint(results)

    def _collect_results_from_builds(self, build_indices):
        return [self._collect_results_from_single_build(index) for index in build_indices]

    def _collect_results_from_single_build(self, build_index):
        build_name = self._build_explorer.get_build_name(build_index)
        scores = self._build_explorer.get_data(build_index).get_evaluation_scores()
        return {'build_name': build_name, 'scores': scores}

def main():
    logger = Utils.get_logger(__name__)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--buildpath', '-b', dest='buildpath', type=str, default=os.environ.get("WIKIMAP_BUILDPATH", None),
        help="Specify a directory where builds are located. Can also be set by WIKIMAP_BUILDPATH environment variable.")
    parser.add_argument('--reportpath', '-r', dest='reportpath', type=str, default=os.environ.get("WIKIMAP_REPORTPATH", None),
        help="Specify a directory where report files should be placed. Can also be set by WIKIMAP_REPORTPATH environment variable.")
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
        build_explorer = BuildExplorer(args.buildpath, args.prefix)
        creator = ReportCreator(build_explorer)
        creator.print_results(args.indices)

    except Exception, e:
        logger.exception(e)
        raise

if __name__ == '__main__':
    Utils.config_logging()
    main()
