#!/usr/bin/env python

import os
import sys
import argparse
import wikimap
from itertools import imap


class GridSearch(object):
    """
    This class iterates through different combinations of parameters.

    For each argument a value or a list of values is given. At each step of the
    iteration one value from each list is chosen.
    """

    def __init__(self, grid_args):
        """
        Initialize the grid search.

        `grid_args` is an iterable of pairs consisting of a name of an argument
                    and a list of possible values (or a single value)
        """
        self._grid_args = [
            (arg_name, self._maybe_wrap_with_list(arg_values))
            for (arg_name, arg_values)
            in grid_args
            if arg_values]

        self.max_config_num = max(sum(1 for _ in self), 1)

    def __iter__(self):
        """
        Iterate configs.

        Each value in _grid_args is a list. Each step of iteration yields
        a different combination of elements from lists (with one element per
        list at the same time).
        """
        def recursive_iterator(grid):
            if not grid:
                yield []
            else:
                key, value_axis = grid[0]
                for value in value_axis:
                    for tail in recursive_iterator(grid[1:]):
                        yield [(key, value)] + tail

        if not self._grid_args:
            return iter([{}])  # default config
        else:
            return imap(dict, iter(recursive_iterator(self._grid_args)))

    def _maybe_wrap_with_list(self, value):
        if isinstance(value, list):
            return value
        else:
            return [value]


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--target', '-t',
        dest='target_jobs',
        default=wikimap.DEFAULT_TARGET_JOBS,
        type=wikimap.Utils.parse_comma_separated_strings,
        help="Choose jobs to do. Their dependencies will also be included.")
    parser.add_argument(
        '--forced', '-f',
        dest='forced_jobs',
        default=wikimap.DEFAULT_FORCED_JOBS,
        type=wikimap.Utils.parse_comma_separated_strings,
        help=("Add targets (like '-t' option) but also mark them for "
              "recomputation, even if their results could be copied from "
              "previous runs."))
    parser.add_argument(
        '--buildpath', '-b',
        type=str,
        default=os.environ.get("WIKIMAP_BUILDPATH", None),
        help=("Choose a directory for builds. Each build will create a new "
              "subdirectory inside. Can also be set by WIKIMAP_BUILDPATH "
              "environment variable."))
    parser.add_argument(
        '--prefix', '-p',
        type=str,
        default='build',
        help="Choose a prefix for subdirectories inside the builds directory.")
    parser.add_argument(
        '--lang',
        dest='meta.language',
        type=wikimap.Utils.parse_comma_separated_strings,
        default=wikimap.DEFAULT_LANGUAGE,
        help="Choose the edition of wikipedia to use.")
    parser.add_argument(
        '--base',
        dest='base_build_index',
        type=int,
        default=-1,
        help=("Choose an index of a base build. The program will try to skip "
              "parts of the build if it thinks they would have the same "
              "results. By default the last build is used."))
    parser.add_argument(
        '--print-config',
        action='store_true',
        help="Print the full configuration of the build and quit.")
    parser.add_argument(
        '--print-jobs',
        action='store_true',
        help="Print a list of jobs included in the build and quit.")
    parser.add_argument(
        '--ldnn.neighbors_count',
        type=wikimap.Utils.parse_comma_separated_ints,
        default=wikimap.DEFAULT_NEAREST_NEIGHBORS_COUNT,
        help=("Choose a number of nearest neighbors computed for each point "
              "in map. Can also be a comma-separated list of ints."))
    parser.add_argument(
        '--embed.context_size',
        type=wikimap.Utils.parse_comma_separated_ints,
        default=wikimap.DEFAULT_CONTEXT_SIZE,
        help=("Choose a context size of word embedding method. Can also be "
              "a comma-separated list of ints."))
    parser.add_argument(
        '--embed.backtrack_probability',
        type=wikimap.Utils.parse_comma_separated_floats,
        default=wikimap.DEFAULT_BACKTRACK_PROBABILITY,
        help=("Choose a probability of backtracking in a random walk "
              "through link graph. Can also be a comma-separated list of "
              "floats."))
    parser.add_argument(
        '--embed.dimension',
        type=wikimap.Utils.parse_comma_separated_ints,
        default=wikimap.DEFAULT_DIMENSION,
        help=("Choose a dimension of embeddings. Can also be a "
              "comma-separated list of ints."))
    parser.add_argument(
        '--embed.walks_per_node',
        type=wikimap.Utils.parse_comma_separated_ints,
        default=wikimap.DEFAULT_WALKS_PER_NODE,
        help=("Choose a number of random walks per node in graph-based "
              "embedding algorithms. Can also be a comma-separated list of "
              "ints."))
    parser.add_argument(
        '--embed.method',
        type=wikimap.Utils.parse_comma_separated_strings,
        default=wikimap.DEFAULT_EMBEDDING_METHOD,
        help=("Choose an embedding method. Has to be one of the following: "
              "{}. Can also be a comma-separated list of the above.".format(
                ', '.join(wikimap.EMBEDDING_METHODS))))
    parser.add_argument(
        '--embed.node_count',
        type=wikimap.Utils.parse_comma_separated_ints,
        default=wikimap.DEFAULT_EMBEDDING_NODE_COUNT,
        help=("Choose a number of embedded nodes (wikipedia titles). Can also "
              "be a comma-separated list of ints."))
    parser.add_argument(
        '--embed.epochs_count',
        type=wikimap.Utils.parse_comma_separated_ints,
        default=wikimap.DEFAULT_EPOCH_COUNT,
        help=("Choose a number of epochs to use during training. Can also be "
              "a comma=separated list of ints."))
    parser.add_argument(
        '--embed.walk_length',
        type=wikimap.Utils.parse_comma_separated_ints,
        default=wikimap.DEFAULT_WALK_LENGTH,
        help=("Choose a maximum walk length of random walks during embedding. "
              "Can also be a comma-separated list of ints."))

    args = parser.parse_args()

    if not args.buildpath:
        sys.exit("Choose a build path, by using --buildpath (-b) option or by "
                 "setting the WIKIMAP_BUILDPATH environment variable.")

    wikimap.Utils.config_logging()
    logger = wikimap.Utils.get_logger(__name__)

    grid_arg_names = [
        'ldnn.neighbors_count', 'embed.context_size', 'embed.walks_per_node',
        'embed.backtrack_probability', 'embed.dimension', 'embed.node_count',
        'embed.method', 'embed.epochs_count', 'embed.walk_length',
        'meta.language']
    grid_args = [
        (arg_name, value_list)
        for (arg_name, value_list)
        in vars(args).iteritems()
        if arg_name in grid_arg_names]
    build_configs = GridSearch(grid_args)

    for config_no, config in enumerate(build_configs):
        build = wikimap.Build(
            builds_dir=args.buildpath,
            build_prefix=args.prefix,
            base_build_index=args.base_build_index,
            target_jobs=args.target_jobs,
            forced_jobs=args.forced_jobs,
            config=config)

        if args.print_jobs:
            build.print_jobs()
        elif args.print_config:
            build.print_config()
        else:
            logger.important(wikimap.Utils.thick_line_separator)
            format_str = 'STARTING BUILD [{{:{}}}/{{}}]'.format(
                wikimap.Utils.get_number_width(build_configs.max_config_num))
            logger.important(format_str.format(
                config_no + 1,
                build_configs.max_config_num))

            build.run()


if __name__ == "__main__":
    main()
