class InvalidIntRangeException(Exception):
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
            raise InvalidIntRangeException("Too many colons in range expression.")
        step = int(nums[2]) if len(nums) == 3 else 1
        return range(int(nums[0]), int(nums[1]), step)
    else: # comma case
        return [int(num) for num in string.split(',')]
