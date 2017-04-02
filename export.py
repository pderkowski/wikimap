#!/usr/bin/env python

import argparse
import os
import sys
from wikimap import Utils, BuildExplorer

def export(files, dest_dir):
    dest_dir = os.path.realpath(dest_dir)
    dest_path = os.path.join(dest_dir, 'build.tar.gz')
    print 'EXPORTING RESULTS TO {}'.format(dest_path)
    Utils.make_dir_if_not_exists(dest_dir)
    if os.path.exists(dest_path):
        os.unlink(dest_path)
    Utils.pack(files, dest_dir, dest_path)

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--buildpath', '-b', dest='buildpath', type=str, default=os.environ.get("WIKIMAP_BUILDPATH", None),
        help="Specify a directory where builds are located. Can also be set by WIKIMAP_BUILDPATH environment variable.")
    parser.add_argument('--prefix', '-p', dest='prefix', type=str, default='build',
        help="Specify a prefix of subdirectories inside the builds directory.")
    parser.add_argument('--index', '-i', dest='build_index', default=-1, type=int,
        help="Choose an index if you want to export a specific build. Otherwise the last build will be exported.")
    args = parser.parse_args()

    if not args.buildpath:
        sys.exit("Specify the build path, using --buildpath (-b) option or by setting the WIKIMAP_BUILDPATH environment variable.")

    export_dir = './bin'

    build_explorer = BuildExplorer(args.buildpath, args.prefix)
    P = build_explorer.get_paths(args.build_index)
    exported_files = [P.wikimap_points, P.wikimap_categories, P.zoom_index, P.metadata, P.aggregated_inlinks, P.aggregated_outlinks]
    export(exported_files, export_dir)

if __name__ == '__main__':
    Utils.config_logging(log_length="minimal")
    main()
