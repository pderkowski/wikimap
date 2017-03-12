#!/usr/bin/env python

import os
import sys
import argparse
from wikimap import Utils
from wikimap import Builder, Builds

def get_tag_2_num(build):
    tag_2_num = {}
    for job in build:
        if len(job.tag) > 0:
            tag_2_num[job.tag] = job.number
    return tag_2_num

def replace_tags_with_nums(string, build):
    tag_2_num = get_tag_2_num(build)
    tags = tag_2_num.keys()
    tags.sort(key=len, reverse=True)
    for tag in tags:
        string = string.replace(tag, str(tag_2_num[tag]))
    return string

def parse_job_ranges(ranges, build):
    max_job_number = len(build) - 1
    num_only_ranges = replace_tags_with_nums(ranges, build)
    range_strings = num_only_ranges.split(',')
    jobs_in_ranges = []
    for rs in range_strings:
        rs = rs.strip()
        sep_pos = rs.find('-')
        if sep_pos == -1:
            if rs == '*':
                jobs_in_ranges.extend(range(0, max_job_number+1))
            elif rs == '':
                pass
            else:
                jobs_in_ranges.append(int(rs))
        elif sep_pos == 0:
            jobs_in_ranges.extend(range(0, int(rs[1:]) + 1))
        elif sep_pos == len(rs) - 1:
            jobs_in_ranges.extend(range(int(rs[:-1]), max_job_number + 1))
        else:
            jobs_in_ranges.extend(range(int(rs[:sep_pos]), int(rs[sep_pos+1:]) + 1))
    return set(jobs_in_ranges)

def list_jobs(build):
    table = Utils.make_table(['#', 'TAG', 'JOB NAME'], ['r', 'l', 'l'], [[str(job.number), job.tag, job.name] for job in build])
    print table.get_string()

def main():
    Utils.config_logging()

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
    parser.add_argument('--base', dest='base_build_index', type=int,
        help="Choose the index of a 'base' build.")
    args = parser.parse_args()

    if not args.buildpath:
        sys.exit("Specify the build path, using --buildpath (-b) option or by setting the WIKIMAP_BUILDPATH environment variable.")

    Builder.set_builds_dir(args.buildpath, args.prefix)
    if args.base_build_index:
        Builder.set_base_build(args.base_build_index)

    build = {
        'en': Builds.English,
        'pl': Builds.Polish
    }[args.language]

    target_jobs = parse_job_ranges(args.target_jobs, build)
    forced_jobs = parse_job_ranges(args.forced_jobs, build)

    build.configure(target_jobs, forced_jobs)

    if args.list_jobs:
        list_jobs(build)
    else:
        Builder.run_build(build)

if __name__ == "__main__":
    main()
