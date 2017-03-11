#!/usr/bin/env python

import os
import sys
import argparse
from wikimap import Utils
from wikimap import Build, Builder

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
    max_job_number = len(build.jobs) - 1
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

def list_jobs(build, plan):
    included_jobs, _ = plan
    rows = [[str(job.number), job.tag, job.name] for job in build if included_jobs[job.number]]
    table = Utils.make_table(['#', 'TAG', 'JOB NAME'], ['r', 'l', 'l'], rows)
    print table.get_string()

def main():
    Utils.configLogging()

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--list', '-l', dest='list_jobs', action='store_true',
        help="Print a list of jobs included in the build together with the build plan.")
    parser.add_argument('--target', '-t', dest='target', type=str, default='*',
        help="Specify which jobs to perform. All of their dependencies will also be included.")
    parser.add_argument('--force', '-f', dest='force', type=str, default='',
        help="Add targets (like '-t' option) but also mark them for recomputation, even if their results could be copied from previous runs.")
    parser.add_argument('--buildpath', '-b', dest='buildpath', type=str, default=os.environ.get("WIKIMAP_BUILDPATH", None),
        help="Specify a directory for builds. Each build will create a new subdirectory inside. Can also be set by WIKIMAP_BUILDPATH environment variable.")
    parser.add_argument('--prefix', '-p', dest='prefix', type=str, default='build',
        help="Specify a prefix for subdirectories inside the builds directory.")
    args = parser.parse_args()

    if not args.buildpath:
        sys.exit("Specify the build path, using --buildpath (-b) option or by setting the WIKIMAP_BUILDPATH environment variable.")

    Builder.set_builds_dir(args.buildpath, args.prefix)

    build = Build.Build()
    targets = parse_job_ranges(args.target, build)
    forced = parse_job_ranges(args.force, build)
    plan = Builder.get_build_plan(build, targets, forced)

    if args.list_jobs:
        list_jobs(build, plan)
    else:
        Builder.run_build(build, plan)

if __name__ == "__main__":
    main()
