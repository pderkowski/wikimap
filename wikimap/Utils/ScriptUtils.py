import numpy as np

class ParseException(Exception):
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

def parse_comma_separated_strings(string):
    return string.split(',')
