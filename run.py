#!/usr/bin/env python

import os
import sys
import logging
import argparse
from prettytable import PrettyTable
from wikimap import Utils
from wikimap.BuildManager import BuildManager
from wikimap import Build

def parse_noskip(noskip_arg, max_number):
    parts = noskip_arg.split(',')
    noskipped = []
    for p in parts:
        p = p.strip()
        split = p.find('-')
        if split == -1: # p is like '12'
            noskipped.append(int(p))
        elif split == 0: # p is like '-12'
            noskipped.extend(range(0, int(p[1:]) + 1))
        elif split == len(p) - 1: # p is like '12-'
            noskipped.extend(range(int(p[:-1]), max_number + 1))
        else: # p is like '1-12'
            noskipped.extend(range(int(p[:split]), int(p[split+1:]) + 1))
    return noskipped

def replace_tags_with_nums(string, tag_2_num):
    tags = tag_2_num.keys()
    tags.sort(key=len, reverse=True)
    for tag in tags:
        string = string.replace(tag, str(tag_2_num[tag]))
    return string

def list_jobs(build):
    table = PrettyTable(['#', 'TAG', 'JOB NAME'])
    table.align['#'] = 'r'
    table.align['TAG'] = 'l'
    table.align['JOB NAME'] = 'l'

    for i, s in enumerate(build):
        table.add_row([str(i), s.tag, s.name])

    print table.get_string()

def get_tag_2_num(build):
    tag_2_num = {}
    for num, job in enumerate(build):
        if len(job.tag) > 0:
            tag_2_num[job.tag] = num
    return tag_2_num

def main():
    Utils.configLogging()

    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', dest='list_jobs', action='store_true',
        help="print a list of jobs included in a build")
    parser.add_argument('--noskip', nargs='?', dest='noskip', type=str,
        help="specify which build steps should not be skipped even if otherwise they would be")
    args = parser.parse_args()

    build = Build.Build()
    tag_2_num = get_tag_2_num(build)

    if args.noskip is not None:
        num_only_arg = replace_tags_with_nums(args.noskip, tag_2_num)
        for n in parse_noskip(num_only_arg, len(build.jobs) - 1):
            build[n].noskip = True

    if args.list_jobs:
        list_jobs(build)
    elif "BUILDPATH" not in os.environ:
        print "Set the BUILDPATH environment variable to the directory where the program will place the generated files."
        sys.exit(1)
    else:
        manager = BuildManager(os.environ["BUILDPATH"])
        build.set_build_dir(manager.newBuild)
        manager.run(build)

if __name__ == "__main__":
    main()
