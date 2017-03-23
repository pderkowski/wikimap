#!/usr/bin/env python

import os
import sys
import ast
import argparse
from wikimap import Utils
from wikimap import Builder, Builds

class BuildArgumentParser(object):
    def __init__(self, build):
        self._build = build

    def parse_job_ranges(self, multi_range_string):
        max_job_number = len(self._build) - 1
        num_only_ranges = self._replace_tags_with_nums(multi_range_string)
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

    def parse_config(self, config_string):
        config = ast.literal_eval(config_string) # literal_eval only evaluates basic types instead of arbitrary code
        for job_name_or_tag, job_config in config.iteritems():
            del config[job_name_or_tag]
            config[self._replace_tag_with_name(job_name_or_tag)] = job_config
        return config

    def _replace_tags_with_nums(self, string):
        tag_2_num = self._get_tag_2_num()
        tags = tag_2_num.keys()
        tags.sort(key=len, reverse=True)
        for tag in tags:
            string = string.replace(tag, str(tag_2_num[tag]))
        return string

    def _replace_tag_with_name(self, string):
        tag_2_name = self._get_tag_2_name()
        return tag_2_name[string] if string in tag_2_name else string

    def _get_tag_2_num(self):
        tag_2_num = {}
        for job in self._build:
            if len(job.tag) > 0:
                tag_2_num[job.tag] = job.number
        return tag_2_num

    def _get_tag_2_name(self):
        tag_2_name = {}
        for job in self._build:
            if len(job.tag) > 0:
                tag_2_name[job.tag] = job.name
        return tag_2_name

def list_jobs(build):
    print Utils.make_table(['#', 'TAG', 'JOB NAME'], [[str(job.number), job.tag, job.name] for job in build], ['r', 'l', 'l'])

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
    parser.add_argument('--config', '-c', dest='config', type=argparse.FileType('r'),
        help="Specify a configuration file. Its values will overwrite default parameters of jobs.")
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

    build_arg_parser = BuildArgumentParser(build)

    target_jobs = build_arg_parser.parse_job_ranges(args.target_jobs)
    forced_jobs = build_arg_parser.parse_job_ranges(args.forced_jobs)
    config = build_arg_parser.parse_config(args.config.read()) if args.config else {}

    build.plan(target_jobs, forced_jobs)
    build.configure(config)

    if args.list_jobs:
        list_jobs(build)
    else:
        Builder.run_build(build)

if __name__ == "__main__":
    main()
