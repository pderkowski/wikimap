import logging
import Utils
import contextlib
import sqlite3

def connect(*tables):
    tables = list(tables)

    con = sqlite3.connect(tables[0])

    con.execute("PRAGMA synchronous = OFF")
    con.execute("PRAGMA journal_mode = OFF")
    con.execute("PRAGMA cache_size = 10000000")

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
    def __init__(self, *paths):
        self._paths = paths

    def execute(self, query):
        with self._setup(query) as con:
            con.execute(query._query)
            con.commit()

    def executemany(self, query, values):
        with self._setup(query) as con:
            con.executemany(query._query, values)
            con.commit()

    def select(self, query):
        with self._setup(query) as con:
            cursor = con.cursor()
            cursor.execute(query._query)
            return cursor

    @contextlib.contextmanager
    def _setup(self, query):
        logger = logging.getLogger(__name__)

        if query._logStart:
            logger.info("Starting {}".format(query._description))

        con = connect(*self._paths)

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


class PageTable(TableProxy):
    def __init__(self, pageTablePath):
        super(PageTable, self).__init__(pageTablePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE page (
                page_id             INTEGER    NOT NULL                PRIMARY KEY,
                page_namespace      INTEGER    NOT NULL  DEFAULT '0',
                page_title          TEXT       NOT NULL  DEFAULT ''
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO page VALUES (?,?,?)", "populating page table", logStart=True), values)
        self.execute(Query("CREATE UNIQUE INDEX ns_title_idx ON page(page_namespace, page_title)", "creating index ns_title_idx in page table", logStart=True, logProgress=True))

class LinksTable(TableProxy):
    def __init__(self, linksTablePath):
        super(LinksTable, self).__init__(linksTablePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE links (
                pl_from             INTEGER    NOT NULL  DEFAULT '0',
                pl_namespace        INTEGER    NOT NULL  DEFAULT '0',
                pl_title            TEXT       NOT NULL  DEFAULT '',
                pl_from_namespace   INTEGER    NOT NULL  DEFAULT '0'
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO links VALUES (?,?,?,?)", "populating links table", logStart=True), values)
        self.execute(Query("CREATE INDEX from_id_idx ON links(pl_from);", "creating index from_id_idx in links table", logStart=True, logProgress=True))
        self.execute(Query("CREATE INDEX ns_title_idx ON links(pl_namespace, pl_title);", "creating index ns_title_idx in links table", logStart=True, logProgress=True))

class CategoryTable(TableProxy):
    def __init__(self, categoryTablePath):
        super(CategoryTable, self).__init__(categoryTablePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE category (
                cat_id         INTEGER     NOT NULL                PRIMARY KEY,
                cat_title      TEXT        NOT NULL    DEFAULT ''
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO category VALUES (?,?)", "populating category table", logStart=True), values)
        self.execute(Query('CREATE UNIQUE INDEX title_idx ON category(cat_title);', "creating index title_idx in category table", logStart=True, logProgress=True))

class CategoryLinksTable(TableProxy):
    def __init__(self, categoryLinksTablePath):
        super(CategoryLinksTable, self).__init__(categoryLinksTablePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE categorylinks (
                cl_from      INTEGER     NOT NULL    DEFAULT '0',
                cl_to        TEXT        NOT NULL    DEFAULT ''
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO categorylinks VALUES (?,?)", "populating categorylinks table", logStart=True), values)
        self.execute(Query('CREATE UNIQUE INDEX from_to_idx ON categorylinks(cl_from, cl_to);', "creating index from_to_idx in categorylinks table", logStart=True, logProgress=True))
        self.execute(Query('CREATE INDEX to_idx ON categorylinks(cl_to);', "creating index to_idx in categorylinks table", logStart=True, logProgress=True))

class PagePropertiesTable(TableProxy):
    def __init__(self, pagePropertiesPath):
        super(PagePropertiesTable, self).__init__(pagePropertiesPath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE pageprops (
                pp_page        INTEGER     NOT NULL    DEFAULT '0',
                pp_propname    TEXT        NOT NULL    DEFAULT ''
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO pageprops VALUES (?,?)", "populating pageprops table", logStart=True), values)
        self.execute(Query('CREATE INDEX page_idx ON pageprops(pp_page);', "creating index page_idx in pageprops table", logStart=True, logProgress=True))
        self.execute(Query('CREATE INDEX propname_idx ON pageprops(pp_propname);', "creating index propname_idx in pageprops table", logStart=True, logProgress=True))

class NormalizedLinksTable(TableProxy):
    def __init__(self, normalizedLinksPath):
        super(NormalizedLinksTable, self).__init__(normalizedLinksPath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE norm_links (
                nl_from             INTEGER    NOT NULL  DEFAULT '0',
                nl_to               INTEGER    NOT NULL  DEFAULT '0'
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO norm_links VALUES (?,?)", "populating norm_links table", logStart=True), values)

    def selectAll(self):
        return self.select(Query("SELECT * FROM norm_links"))

class PagerankTable(TableProxy):
    def __init__(self, pagerankPath):
        super(PagerankTable, self).__init__(pagerankPath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE pagerank (
                pr_id             INTEGER    NOT NULL   PRIMARY KEY,
                pr_rank           REAL       NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO pagerank VALUES (?,?)", "populating pagerank table", logStart=True), values)
        self.execute(Query('CREATE INDEX rank_idx ON pagerank(pr_rank);', "creating index rank_idx in pagerank table", logStart=True, logProgress=True))

    def selectIdsByDescendingRank(self, idsNo):
        query = Query("""
            SELECT
                pr_id
            FROM
                pagerank
            ORDER BY
                pr_rank DESC
            LIMIT
                {}""".format(idsNo), 'selecting ids by descending rank', logProgress=True)

        return self.select(query)

class TSNETable(TableProxy):
    def __init__(self, tsnePath):
        super(TSNETable, self).__init__(tsnePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE tsne (
                tsne_id         INTEGER     NOT NULL    PRIMARY KEY,
                tsne_x          REAL        NOT NULL,
                tsne_y          REAL        NOT NULL,
                tsne_order      INTEGER     NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO tsne VALUES (?,?,?,?)", "populating tsne table", logStart=True), values)

class Join(TableProxy):
    def __init__(self, *tables):
        super(Join, self).__init__(*tables)

    def selectNormalizedLinks(self):
        query = Query("""
            SELECT
                *
            FROM
                (SELECT
                    pl_from, page_id
                FROM
                    links,
                    page
                WHERE
                    pl_namespace = page_namespace
                AND pl_title = page_title
                ORDER BY
                    pl_namespace ASC,
                    pl_title ASC)
            ORDER BY
                pl_from ASC""", "selecting normalized links", logProgress=True)

        return self.select(query)

    def selectVisualizedPoints(self):
        query = Query("""
            SELECT
                tsne_x, tsne_y, page_title, page_id
            FROM
                tsne,
                page
            WHERE
                tsne_id = page_id
            ORDER BY
                tsne_order ASC
            """)

        return self.select(query)

    def selectVisualizedCategories(self):
        query = Query("""
            SELECT
                cl_to,
                cl_from
            FROM
                categorylinks,
                tsne,
                category
            WHERE cl_to NOT IN
                (SELECT
                    page_title
                FROM
                    page,
                    pageprops
                WHERE
                    page_id = pp_page
                AND pp_propname = 'hiddencat')
            AND cl_to = cat_title
            AND tsne_id = cl_from
            ORDER BY
                cat_id""", "selecting visualized categories", logProgress=True)

        return self.select(query)
