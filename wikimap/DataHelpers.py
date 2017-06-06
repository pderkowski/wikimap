from itertools import imap, groupby, ifilter
from operator import itemgetter
import logging
import Utils

def normalize_word(word):
    return word.lower().replace(u' ', u'_')

def pipe(arg, *funcs):
    for f in funcs:
        arg = f(arg)
        if arg is None:
            print f
    return arg

class PrintIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        def printAndReturn(sth):
            print repr(sth)
            return sth

        return imap(printAndReturn, self.iterator)

class LogIt(object):
    def __init__(self, frequency, start="", end=""):
        self.frequency = frequency
        self.iterator = None
        self.start = start
        self.end = end

    def __call__(self, iterator):
        self.iterator = iterator
        return self

    def __iter__(self):
        logger = logging.getLogger(__name__)

        if self.start:
            logger.info(self.start)

        for (i, e) in enumerate(self.iterator):
            if self.frequency > 0 and i % self.frequency == 0:
                logger.info('Processed {} records'.format(i))
            yield e

        if self.end:
            logger.info(self.end)

class GroupIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        def join(arg):
            k, group = arg
            return (k, [p[1] for p in group])

        return imap(join, groupby(self.iterator, itemgetter(0)))

class JoinIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return imap(lambda e: u' '.join(e)+u'\n', self.iterator)

class DeferIt(object):
    def __init__(self, iteratorFactory):
        self.iteratorFactory = iteratorFactory

    def __iter__(self):
        return iter(self.iteratorFactory())

class StringifyIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return imap(lambda e: map(Utils.any2unicode, e), self.iterator)

class StringifyIt2(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return imap(lambda e: [unicode(str(e[0]), encoding='utf8'), unicode(str(e[1]), encoding='utf8')], self.iterator)

class ColumnIt(object):
    def __init__(self, *columns):
        self.columns = columns
        self.iterator = None

    def __call__(self, iterator):
        self.iterator = iterator
        return self

    def __iter__(self):
        return imap(itemgetter(*self.columns), self.iterator)

class FlipIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return imap(lambda cols: cols[::-1], self.iterator)

class SumIt(object):
    def __init__(self, *columns):
        self.columns = columns
        self.iterator = None

    def __call__(self, iterator):
        self.iterator = iterator
        return self

    def __iter__(self):
        return imap(lambda cols: sum(cols[c] for c in self.columns), self.iterator)

class TupleIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return imap(tuple, self.iterator)

class InIt(object):
    def __init__(self, container, column):
        self.container = container
        self.column = column
        self.iterator = None

    def __call__(self, iterator):
        self.iterator = iterator
        return self

    def __iter__(self):
        return ifilter(lambda record: record[self.column] in self.container, self.iterator)

class NotInIt(object):
    def __init__(self, container, column):
        self.container = container
        self.column = column
        self.iterator = None

    def __call__(self, iterator):
        self.iterator = iterator
        return self

    def __iter__(self):
        return ifilter(lambda record: record[self.column] not in self.container, self.iterator)

class NotEqualIt(object):
    def __init__(self, val, column):
        self.val = val
        self.column = column
        self.iterator = None

    def __call__(self, iterator):
        self.iterator = iterator
        return self

    def __iter__(self):
        return ifilter(lambda record: record[self.column] != self.val, self.iterator)

class NotCommentIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return ifilter(lambda line: not line.startswith('#'), self.iterator)

class NotBlankIt(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        return ifilter(lambda line: not line.isspace(), self.iterator)
