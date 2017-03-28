#!/usr/bin/env python

import os
import sys
import argparse
from wikimap import Utils, BuildCreator

def list_jobs(build):
    print Utils.make_table(['#', 'TAG', 'JOB NAME'], [[str(job.number), job.tag, job.name] for job in build], ['r', 'l', 'l'])

def main(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--list', '-l', dest='list_jobs', action='store_true',
        help="Print a list of jobs included in the build.")
    parser.add_argument('--target', '-t', dest='target_jobs', type=str, default='*',
        help="Specify which jobs to perform. All of their dependencies will also be included.")
    parser.add_argument('--forced', '-f', dest='forced_jobs', type=str, default='',
        help="Add targets (like '-t' option) but also mark them for recomputation, even if their results could be copied from previous runs.")
    parser.add_argument('--buildpath', '-b', dest='buildpath', type=str, default=os.environ.get("WIKIMAP_BUILDPATH", None),
        help="Specify a directory for builds. Each build will create a new subdirectory inside. Can also be set by WIKIMAP_BUILDPATH environment variable.")
    parser.add_argument('--prefix', '-p', dest='prefix', type=str, default='build',
        help="Specify a prefix for subdirectories inside the builds directory.")
    parser.add_argument('--lang', dest='language', type=str, choices=['en', 'pl'], default='en',
        help="Choose a language of wikipedia to use. Some options may only be available in specific versions.")
    parser.add_argument('--base', dest='base_build_index', type=int, default=-1,
        help="Choose the index of a 'base' build. By default the last one will be used.")
    parser.add_argument('--config', '-c', dest='config', type=argparse.FileType('r'),
        help="Specify a configuration file. Its values will overwrite default parameters of jobs.")

    args = parser.parse_args(argv)

    if not args.buildpath:
        sys.exit("Specify the build path, using --buildpath (-b) option or by setting the WIKIMAP_BUILDPATH environment variable.")

    build_creator = BuildCreator(
        builds_dir=args.buildpath,
        build_prefix=args.prefix,
        base_build_index=args.base_build_index,
        language=args.language,
        target_jobs=args.target_jobs,
        forced_jobs=args.forced_jobs,
        config=args.config.read() if args.config else r"{}")

    if args.list_jobs:
        list_jobs(build_creator.get_build())
    else:
        build_creator.run()

if __name__ == "__main__":
    Utils.config_logging()
    main(sys.argv[1:])
