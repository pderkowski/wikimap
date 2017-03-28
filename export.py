#!/usr/bin/env python

import argparse
import os
import sys
from wikimap import Utils, BuildExplorer

def export(files, dest_dir):
    dest_dir = os.path.realpath(dest_dir)
    print 'EXPORTING RESULTS TO {}'.format(dest_dir)
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    Utils.clear_directory(dest_dir)
    Utils.pack(files, dest_dir, 'build.tar.gz')

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--buildpath', '-b', dest='buildpath', type=str, default=os.environ.get("WIKIMAP_BUILDPATH", None),
        help="Specify a directory where builds are located. Can also be set by WIKIMAP_BUILDPATH environment variable.")
    parser.add_argument('--exportpath', '-e', dest='exportpath', type=str, default=os.environ.get("WIKIMAP_EXPORTPATH", None),
        help="Specify a directory to which files should be exported. Can also be set by WIKIMAP_EXPORTPATH environment variable.")
    parser.add_argument('--prefix', '-p', dest='prefix', type=str, default='build',
        help="Specify a prefix of subdirectories inside the builds directory.")
    parser.add_argument('--index', '-i', dest='build_index', default=-1, type=int,
        help="Choose an index if you want to export a specific build. Otherwise the last build will be exported.")
    args = parser.parse_args()

    if not args.buildpath:
        sys.exit("Specify the build path, using --buildpath (-b) option or by setting the WIKIMAP_BUILDPATH environment variable.")

    if not args.exportpath:
        sys.exit("Specify the export path, using --exportpath (-e) option or by setting the WIKIMAP_EXPORTPATH environment variable.")

    build_explorer = BuildExplorer(args.buildpath, args.prefix)
    P = build_explorer.get_paths(args.build_index)
    exported_files = [P.wikimap_points, P.wikimap_categories, P.zoom_index, P.metadata, P.aggregated_inlinks, P.aggregated_outlinks]
    export(exported_files, args.exportpath)

if __name__ == '__main__':
    Utils.config_logging(log_length="minimal")
    main()
