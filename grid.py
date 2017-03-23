#!/usr/bin/env python

import argparse
import run
from collections import defaultdict
from wikimap import Utils
from pprint import pprint
from tempfile import NamedTemporaryFile

class GridSearch(object):
    def __init__(self, grid_config):
        self._grid_config = list((arg_name, arg_values) for (arg_name, arg_values) in grid_config if arg_values is not None)
        for arg_name, arg_values in self._grid_config:
            assert isinstance(arg_values, list), "Grid values must be lists."
            assert arg_name.count('.') == 1, "Nested and unnamed arguments not allowed. Should be '<job_name>.<job_arg_name>'."

    def run(self, run_args):
        for flat_config in self._iter_configs():
            with NamedTemporaryFile() as tmp_config_file:
                formatted_config = self._format_config(flat_config)
                pprint(formatted_config, tmp_config_file)
                tmp_config_file.flush()
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
        return iter(recursive_iterator(self._grid_config))

    def _format_config(self, flat_config):
        formatted_config = defaultdict(dict)
        for arg_name, arg_value in flat_config:
            arg_name_parts = arg_name.split('.')
            job_name, job_arg_name = arg_name_parts
            formatted_config[job_name][job_arg_name] = arg_value
        return dict(formatted_config)

def parse_int_range(string):
    """
    Two types of strings allowed:
    - comma-separated list of ints (e.g. '7' or '7,12,1')
    - range in the form of <int>:<int> or <int>:<int>:<int> (e.g '1:5' or '1:5:2')
        the first int is the inclusive lower bound, the second the exclusive upper bound
        and the optional third is the step (if missing it is 1)
    """
    if string.find(':'): # colon case
        nums = string.split(':')
        assert len(nums) in range(2, 4), "Too many colons in range expression."
        step = int(nums[2]) if len(nums) == 3 else 1
        return range(int(nums[0]), int(nums[1]), step)
    else: # comma case
        return [int(num) for num in string.split(',')]

def main():
    Utils.config_logging()

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--ldnn.neighbors_count', type=parse_int_range,
        help='Specify a range of ints that will be set as the neighbors_count argument of the ldnn job.')

    known_args, unknown_args = parser.parse_known_args()
    grid_search = GridSearch(vars(known_args).iteritems())
    grid_search.run(unknown_args)

if __name__ == "__main__":
    main()
