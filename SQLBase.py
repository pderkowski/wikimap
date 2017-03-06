import sqlite3
import logging
import Utils
import contextlib

def list2string(lst):
    return repr(lst)

def string2list(string):
    return eval(string)

sqlite3.register_adapter(list, list2string)
sqlite3.register_converter("LIST", string2list)

def connect(*tables, **kwargs):
    tables = list(tables)

    con = sqlite3.connect(tables[0], **kwargs)

    con.execute("PRAGMA synchronous = OFF")
    con.execute("PRAGMA journal_mode = OFF")
    con.execute("PRAGMA cache_size = 20000000")

    con.commit()

    for (i, elem) in enumerate(tables[1:], start=1):
        if isinstance(elem, tuple):
            table = elem[0]
            alias = elem[1]
        else:
            table = elem
            alias = 'db'+str(i)

        con.execute('ATTACH DATABASE ? AS '+alias, (table,))

    con.commit()

    return con

def explain(connection, statement):
    logger = logging.getLogger(__name__)

    cursor = connection.cursor()

    logger.info('Query plan:')
    cursor.execute("EXPLAIN QUERY PLAN "+statement)
    for row in cursor:
        print row

class Query(object):
    def __init__(self, query, description="query", logStart=False, logExplain=False, logProgress=False, logEnd=False):
        self._query = query
        self._description = description
        self._logStart = logStart
        self._logExplain = logExplain
        self._logProgress = logProgress
        self._logEnd = logEnd

class TableProxy(object):
    def __init__(self, *paths, **kwargs):
        self._paths = paths

        useCustomTypes = kwargs.pop('useCustomTypes', False)
        self._detect_types = sqlite3.PARSE_DECLTYPES if useCustomTypes else 0

    def execute(self, query, params=()):
        with self._setup(query) as con:
            con.execute(query._query, params)
            con.commit()

    def executemany(self, query, values):
        with self._setup(query) as con:
            con.executemany(query._query, values)
            con.commit()

    def select(self, query, params=()):
        with self._setup(query) as con:
            cursor = con.cursor()
            cursor.execute(query._query, params)
            return cursor

    @contextlib.contextmanager
    def _setup(self, query):
        logger = logging.getLogger(__name__)

        if query._logStart:
            logger.info("Starting {}".format(query._description))

        con = connect(*self._paths, detect_types=self._detect_types)

        if query._logExplain:
            explain(con, query._query)

        progressHandler = Utils.DumbProgressBar()
        if query._logProgress:
            con.set_progress_handler(progressHandler.report, 100000)

        yield con #execute specific code

        if query._logProgress:
            progressHandler.cleanup()

        if query._logEnd:
            logger.info("Finished {}.".format(query._description))
