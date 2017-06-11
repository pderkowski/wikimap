#!/usr/bin/env python

import argparse
import run
from wikimap import Utils
from pprint import pprint
from tempfile import NamedTemporaryFile
from itertools import imap

class GridSearch(object):
    def __init__(self, grid_config):
        self._logger = Utils.get_logger(__name__)
        self._grid_config = list((arg_name, arg_values) for (arg_name, arg_values) in grid_config if arg_values is not None)
        for arg_name, arg_values in self._grid_config:
            assert isinstance(arg_values, list), "Grid values must be lists."
            assert arg_name.count('.') == 1, "Nested and unnamed arguments not allowed. Should be '<job_name>.<job_arg_name>'."

    def run(self, run_args):
        for config_num, config in enumerate(self._iter_configs()):
            with NamedTemporaryFile() as tmp_config_file:
                pprint(config)
                pprint(config, tmp_config_file)
                tmp_config_file.flush()
                self._log_build_start(config_num + 1, self._count_configs())
                run.main(run_args + ['-c', tmp_config_file.name])

    def _iter_configs(self):
        def recursive_iterator(grid):
            if not grid:
                yield []
            else:
                key, value_axis = grid[0]
                for value in value_axis:
                    for tail in recursive_iterator(grid[1:]):
                        yield [(key, value)] + tail
        return imap(dict, iter(recursive_iterator(self._grid_config)))

    def _count_configs(self):
        return sum(1 for _ in self._iter_configs())

    def _log_build_start(self, config_num, max_config_num):
        self._logger.important(Utils.thick_line_separator)
        format_str = 'STARTING BUILD [{{:{}}}/{{}}]'.format(Utils.get_number_width(max_config_num))
        self._logger.important(format_str.format(config_num, max_config_num))

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--ldnn.neighbors_count', type=Utils.parse_int_range,
        help='Specify a range of ints that will be set as the neighbors_count argument of the ldnn job.')
    parser.add_argument('--embed.context_size', type=Utils.parse_int_range,
        help='Specify a range of ints that will be set as the context_size argument of the embed job.')
    parser.add_argument('--embed.backtrack_probability', type=Utils.parse_float_range,
        help='Specify a range of floats that will be set as the backtrack_probability argument of the embed job.')
    parser.add_argument('--embed.dimensions', type=Utils.parse_int_range,
        help='Specify a range of ints that will be set as the dimensions argument of the embed job.')
    parser.add_argument('--embed.walks_per_node', type=Utils.parse_int_range,
        help='Specify a range of ints that will be set as the walks_per_node argument of the embed job.')
    parser.add_argument('--embed.method', type=Utils.parse_comma_separated_strings,
        help='Specify embedding methods to set as the method argument of the embed job.')
    parser.add_argument('--embed.node_count', type=Utils.parse_int_range,
        help='Specify the number of embedded nodes.')
    parser.add_argument('--embed.epochs_count', type=Utils.parse_int_range,
        help='Specify the number of epochs.')
    parser.add_argument('--verbose', '-v', action='store_true',
        help='Increase log verbosity.')

    known_args, unknown_args = parser.parse_known_args()
    grid_arg_names = ['ldnn.neighbors_count', 'embed.context_size',
                      'embed.backtrack_probability', 'embed.dimensions',
                      'embed.walks_per_node', 'embed.method',
                      'embed.node_count', 'embed.epochs_count']
    grid_args = [(arg, val) for (arg, val) in vars(known_args).iteritems() if arg in grid_arg_names]

    Utils.config_logging(verbose=known_args.verbose)

    grid_search = GridSearch(grid_args)
    grid_search.run(unknown_args)

if __name__ == "__main__":
    main()
