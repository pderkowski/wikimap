class ParseException(Exception):
    pass


def parse_comma_separated_ints(string):
    """Parse list of ints from string."""
    try:
        string = string.split()
        if string:
            return [int(num) for num in string.split(',')]
        else:
            return []
    except ValueError:
        raise ParseException(
            "{} not convertible to list of ints.".format(string))


def parse_comma_separated_floats(string):
    """Parse list of floats from string."""
    try:
        string = string.strip()
        if string:
            return [float(num) for num in string.split(',')]
        else:
            return []
    except ValueError:
        raise ParseException(
            "{} not convertible to list of floats.".format(string))


def parse_comma_separated_strings(string):
    string = string.strip()
    if string:
        return string.split(',')
    else:
        return []
