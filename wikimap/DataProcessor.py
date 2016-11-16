import sqlite3
import logging
import pprint
import codecs
import Utils
import Pagerank
import Link2Vec
import operator as op
import itertools
import TSNE
import gzip
import os
import Tools
import StringIO

class TableLoader(object):
    def __init__(self, blueprint):
        self.blueprint = blueprint

    def _createTable(self, path):
        con = sqlite3.connect(path)

        con.execute("DROP TABLE IF EXISTS {}".format(self.blueprint['targetName']))
        con.executescript(self.blueprint["schema"])
        con.commit()

        return con

    def load(self, inputPath, outputPath):
        startPattern = 'INSERT INTO `'+self.blueprint["sourceName"]+'` VALUES '

        def prepareLine(line):
            return line.rstrip()[len(startPattern):-1] # line ends with ;

        logger = logging.getLogger(__name__)
        logger.info("Starting loading the {} table.".format(self.blueprint["targetName"]))

        recordsTotal = 0

        con = self._createTable(outputPath)

        with gzip.GzipFile(inputPath,'r') as input:
            cursor = con.cursor()
            cursor.execute("PRAGMA synchronous = OFF")
            cursor.execute("PRAGMA journal_mode = OFF")
            cursor.execute("PRAGMA cache_size = 10000000")

            for i, line in enumerate(input):
                if i % 100 == 0:
                    logger.info("Processed {} records.".format(recordsTotal))

                if line.startswith(startPattern):
                    prepared = prepareLine(line)

                    records = self.blueprint['parser'](prepared)

                    if records:
                        cursor.executemany("INSERT INTO "+self.blueprint["targetName"]+" VALUES "+self.blueprint["recordPattern"], records)

                        con.commit()

                        recordsTotal += len(records)

        logger.info("Finished loading the {} table. Processed {} lines.".format(self.blueprint['targetName'], recordsTotal))

        for step in self.blueprint['postprocessing']:
            logger.info('Starting '+step+'...')
            con.execute(step)

        return con

def iterateSelection(db, query, logFrequency=None, join=True):
    logger = logging.getLogger(__name__)

    con = sqlite3.connect(db)
    cur = con.cursor()

    cur.execute(query)

    for i, row in enumerate(cur):
        if logFrequency and i % logFrequency == 0:
            logger.info('Processed {} lines'.format(i))

        if join:
            yield ' '.join(map(str, row))+'\n'
        else:
            yield row

def stringify(obj):
    if isinstance(obj, basestring):
        return obj
    else:
        return str(obj)

class GroupIterator(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        for k, group in itertools.groupby(self.iterator, op.itemgetter(0)):
            yield map(stringify, [k] + [p[1] for p in group])

def loadPageTable(pageSqlPath, output):
    blueprint = {
        'sourceName': 'page',
        'targetName': 'page',
        'schema': (
                "CREATE TABLE page (\n"
                "page_id             INTEGER    NOT NULL                PRIMARY KEY,\n"
                "page_namespace      INTEGER    NOT NULL  DEFAULT '0',\n"
                "page_title          TEXT       NOT NULL  DEFAULT '');\n"),
        'recordPattern': '(?,?,?)',
        'parser': Tools.getPageRecords,
        'postprocessing': ['CREATE UNIQUE INDEX ns_title_idx ON page(page_namespace, page_title);']
    }

    pages = TableLoader(blueprint)
    pages.load(pageSqlPath, output)

def loadLinksTable(linksSqlPath, output):
    blueprint = {
        'sourceName': "pagelinks",
        'targetName': "links",
        'schema': (
                "CREATE TABLE links (\n"
                "pl_from             INTEGER    NOT NULL  DEFAULT '0',\n"
                "pl_namespace        INTEGER    NOT NULL  DEFAULT '0',\n"
                "pl_title            TEXT       NOT NULL  DEFAULT '',\n"
                "pl_from_namespace   INTEGER    NOT NULL  DEFAULT '0');\n"),
        'recordPattern': '(?,?,?,?)',
        'parser': Tools.getLinksRecords,
        'postprocessing': ["CREATE INDEX from_id_idx ON links(pl_from);",
            "CREATE INDEX ns_title_idx ON links(pl_namespace, pl_title);"]
    }

    links = TableLoader(blueprint)
    links.load(linksSqlPath, output)

def loadCategoryTable(categorySqlPath, output):
    blueprint = {
        'sourceName': 'category',
        'targetName': 'category',
        'schema': (
                "CREATE TABLE category (\n"
                "cat_id         INTEGER     NOT NULL                PRIMARY KEY,\n"
                "cat_title      TEXT        NOT NULL    DEFAULT '');\n"),
        'recordPattern': '(?,?)',
        'parser': Tools.getCategoryRecords,
        'postprocessing': ['CREATE UNIQUE INDEX title_idx ON category(cat_title);']
    }

    category = TableLoader(blueprint)
    category.load(categorySqlPath, output)

def loadCategoryLinksTable(categoryLinksSqlPath, output):
    blueprint = {
        'sourceName': 'categorylinks',
        'targetName': 'categorylinks',
        'schema': (
                "CREATE TABLE categorylinks (\n"
                "cl_from      INTEGER     NOT NULL    DEFAULT '0',\n"
                "cl_to        TEXT        NOT NULL    DEFAULT '');\n"),
        'recordPattern': '(?,?)',
        'parser': Tools.getCategoryLinksRecords,
        'postprocessing': ['CREATE UNIQUE INDEX from_to_idx ON categorylinks(cl_from, cl_to);',
            'CREATE INDEX to_idx ON categorylinks(cl_to);']
    }

    categoryLinks = TableLoader(blueprint)
    categoryLinks.load(categoryLinksSqlPath, output)

def loadPagePropertiesTable(pagePropertiesSqlPath, output):
    blueprint = {
        'sourceName': 'page_props',
        'targetName': 'pageprops',
        'schema': (
                "CREATE TABLE pageprops (\n"
                "pp_page        INTEGER     NOT NULL    DEFAULT '0',\n"
                "pp_propname    TEXT        NOT NULL    DEFAULT '');\n"),
        'recordPattern': '(?,?)',
        'parser': Tools.getPagePropertiesRecords,
        'postprocessing': ['CREATE INDEX page_idx ON pageprops(pp_page);',
            'CREATE INDEX propname_idx ON pageprops(pp_propname);']
    }

    pageProperties = TableLoader(blueprint)
    pageProperties.load(pagePropertiesSqlPath, output)

def normalizeLinks(pageTablePath, linksTablePath, output):
    logger = logging.getLogger(__name__)

    con = sqlite3.connect(pageTablePath)

    cursor = con.cursor()

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = OFF")
    cursor.execute("PRAGMA cache_size = 10000000")

    con.commit()

    con.execute('ATTACH DATABASE ? AS db2', (linksTablePath,))
    con.execute('ATTACH DATABASE ? AS out', (output,))

    con.execute("""
        CREATE TABLE out.norm_links (
            nl_from             INTEGER    NOT NULL  DEFAULT '0',
            nl_to               INTEGER    NOT NULL  DEFAULT '0'
        );""")

    statement = """
        INSERT INTO
            out.norm_links
        SELECT
            *
        FROM
            (SELECT
                links.pl_from, page.page_id
            FROM
                links,
                page
            WHERE
                links.pl_namespace = page.page_namespace
            AND links.pl_title = page.page_title
            ORDER BY
                links.pl_namespace ASC,
                links.pl_title ASC)
        ORDER BY
            pl_from ASC"""


    logger.info('Query plan:')
    cursor.execute("EXPLAIN QUERY PLAN "+statement)
    for row in cursor:
        print row

    logger.info('Starting link normalization. This may take a couple of hours.')

    progressHandler = Utils.DumbProgressBar()
    con.set_progress_handler(progressHandler.report, 10000000)
    cursor.execute(statement)
    con.commit()

    logger.info('Finished link normalization.')

def computePagerank(normalizedLinksPath, pagerankPath):
    selection = iterateSelection(normalizedLinksPath, "SELECT * FROM norm_links")

    prCon = sqlite3.connect(pagerankPath)
    prCon.execute("""
        CREATE TABLE pagerank (
            pr_id             INTEGER    NOT NULL   PRIMARY KEY,
            pr_rank           REAL       NOT NULL
        );""")

    prCon.executemany("INSERT INTO pagerank VALUES (?, ?)", Pagerank.pagerank(selection))
    prCon.commit()

def computeEmbeddings(normalizedLinksPath, embeddingsPath):
    selection = iterateSelection(normalizedLinksPath, "SELECT * FROM norm_links", join=False)
    Link2Vec.build(GroupIterator(selection), embeddingsPath)

def computeTSNE(embeddingsPath, pagerankPath, tsnePath, pagesNo=10000):
    selection = iterateSelection(pagerankPath, """
        SELECT
            pr_id
        FROM
            pagerank
        ORDER BY
            pr_rank DESC
        LIMIT
            {}""".format(pagesNo), join=False)

    tsneCon = sqlite3.connect(tsnePath)
    tsneCon.execute("""
        CREATE TABLE tsne (
            tsne_id         INTEGER     NOT NULL    PRIMARY KEY,
            tsne_x          REAL        NOT NULL,
            tsne_y          REAL        NOT NULL,
            tsne_order      INTEGER     NOT NULL
        );""")

    tsneCon.executemany("INSERT INTO tsne VALUES (?, ?, ?, ?)", TSNE.run(embeddingsPath, map(op.itemgetter(0), selection)))
    tsneCon.commit()

def selectCategories(categoryLinksPath, categoryPath, pagesPath, tsnePath, pagePropertiesPath, selectedPath):
    logger = logging.getLogger(__name__)

    con = sqlite3.connect(categoryLinksPath)

    cursor = con.cursor()

    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA journal_mode = OFF")
    cursor.execute("PRAGMA cache_size = 10000000")

    con.commit()

    con.execute('ATTACH DATABASE ? AS db2', (pagesPath,))
    con.execute('ATTACH DATABASE ? AS db3', (tsnePath,))
    con.execute('ATTACH DATABASE ? AS db4', (categoryPath,))
    con.execute('ATTACH DATABASE ? AS db5', (pagePropertiesPath,))

    # statement = """
    #     SELECT
    #         cl_to,
    #         page_title
    #     FROM
    #         categorylinks,
    #         tsne,
    #         page
    #     WHERE
    #         tsne_id = cl_from
    #     AND cl_from = page_id
    #     ORDER BY
    #         cl_to ASC
    #     """

    statement = """
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
            cat_id
        """

    # statement = """
    #     SELECT
    #         page_title
    #     FROM
    #         page,
    #         pageprops
    #         -- category
    #     WHERE
    #         page_id = pp_page
    #     -- AND page_namespace = 4
    #     AND pp_propname = 'hiddencat'
    #     LIMIT 100
    #     """

    # cursor.execute(statement)
    # for row in cursor:
    #     print row

    logger.info('Query plan:')
    cursor.execute("EXPLAIN QUERY PLAN "+statement)
    for row in cursor:
        print row

    logger.info('Starting selecting categories.')

    progressHandler = Utils.DumbProgressBar()
    con.set_progress_handler(progressHandler.report, 10000000)

    cursor.execute(statement)

    with codecs.open(selectedPath,'w',encoding='utf8') as output:
        for row in GroupIterator(cursor):
            output.write(u' '.join(row)+'\n')

    logger.info('Finished selecting categories.')

def selectPoints(tsnePath, pagesPath, selectedPath):
    tsneCon = sqlite3.connect(tsnePath)
    tsneCon.execute('ATTACH DATABASE ? AS db2', (pagesPath,))

    cursor = tsneCon.cursor()
    cursor.execute("""
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

    with codecs.open(selectedPath,'w',encoding='utf8') as output:
        for row in cursor:
            output.write(u'{} {} {} {}\n'.format(row[0], row[1], row[2], row[3]))
