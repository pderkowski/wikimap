import numpy as np
import ast
from collections import defaultdict

class ParseException(Exception):
    pass

class InvalidConfigException(Exception):
    pass

def parse_int_range(string):
    """
    Two types of strings allowed:
    - comma-separated list of ints (e.g. '7' or '7,12,1')
    - range in the form of <int>:<int> or <int>:<int>:<int> (e.g '1:5' or '1:5:2')
        the first int is the inclusive lower bound, the second the exclusive upper bound
        and the optional third is the step (if missing it is 1)
    """
    if string.find(':') >= 0: # colon case
        nums = string.split(':')
        if len(nums) not in range(2, 4):
            raise ParseException("Too many colons in range expression.")
        step = int(nums[2]) if len(nums) == 3 else 1
        return range(int(nums[0]), int(nums[1]), step)
    else: # comma case
        return [int(num) for num in string.split(',')]

def parse_float_range(string):
    """
    Two types of strings allowed:
    - comma-separated list of floats (e.g. '7.5' or '7.5,12,1.')
    - range in the form of <int>:<int>:<int> (e.g '0:1:0.1')
        the first int is the inclusive lower bound, the second the exclusive upper bound
        and the third is the step
    """
    if string.find(':') >= 0: # colon case
        nums = string.split(':')
        if len(nums) != 3:
            raise ParseException("Wrong number of colons in range expression.")
        return list(np.arange(float(nums[0]), float(nums[1]), float(nums[2])))
    else: # comma case
        return [float(num) for num in string.split(',')]

class Config(object):
    @staticmethod
    def from_string(string):
        return Config(ast.literal_eval(string))

    def __init__(self, config):
        if not isinstance(config, dict):
            raise InvalidConfigException('Expected a dict.')
        self._config = defaultdict(lambda: None)
        self._config.update(config.iteritems())

    def validate(self, required=None, optional=None):
        required = required or []
        optional = optional or []

        for (arg_name, arg_type) in required:
            if arg_name not in self._config:
                raise InvalidConfigException("Missing required parameter '{}'.".format(arg_name))

        for (arg_name, arg_type) in required + optional:
            if arg_name in self._config and arg_type and not isinstance(self._config[arg_name], arg_type):
                raise InvalidConfigException("Wrong type of parameter '{}'. Expected {}, got {}.".format(
                    arg_name, str(arg_type), str(type(self._config[arg_name]))))

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def get(self):
        return self._config
