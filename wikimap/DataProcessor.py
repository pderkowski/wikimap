import sqlite3
import logging
import pprint
import codecs
import SqliteWrapper
import Utils
import Pagerank
import Link2Vec
import operator as op
import itertools
import TSNE

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
    selection = SqliteWrapper.iterateSelection(normalizedLinksPath, "SELECT * FROM norm_links")

    prCon = sqlite3.connect(pagerankPath)
    prCon.execute("""
        CREATE TABLE pagerank (
            pr_id             INTEGER    NOT NULL   PRIMARY KEY,
            pr_rank           REAL       NOT NULL
        );""")

    prCon.executemany("INSERT INTO pagerank VALUES (?, ?)", Pagerank.pagerank(selection))
    prCon.commit()

def computeEmbeddings(normalizedLinksPath, embeddingsPath):
    class GroupIterator(object): # gensim requires an iterable (that can be re-iterated)
        def __iter__(self):
            selection = SqliteWrapper.iterateSelection(normalizedLinksPath, "SELECT * FROM norm_links", join=False)
            for k, group in itertools.groupby(selection, op.itemgetter(0)):
                yield map(str, [k] + [p[1] for p in group])

    Link2Vec.build(GroupIterator(), embeddingsPath)

def computeTSNE(embeddingsPath, pagerankPath, tsnePath, pagesNo=10000):
    selection = SqliteWrapper.iterateSelection(pagerankPath, """
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


def computeFinalTable(tsnePath, pagesPath, finalPath):
    tsneCon = sqlite3.connect(tsnePath)
    tsneCon.execute('ATTACH DATABASE ? AS db2', (pagesPath,))

    cursor = tsneCon.cursor()
    cursor.execute("""
        SELECT
            tsne_x, tsne_y, page_title
        FROM
            tsne,
            page
        WHERE
            tsne_id = page_id
        ORDER BY
            tsne_order ASC
        """)

    with codecs.open(finalPath,'w',encoding='utf8') as output:
        for row in cursor:
            output.write(u'{} {} {}\n'.format(row[0], row[1], row[2]))

    # tsne = pd.read_table(tsnePath, delim_whitespace=True, header=None, names=['id', 'x', 'y'])
    # dictionary = pd.read_table(pagesPath, delim_whitespace=True, header=None, names=['id', 'title'])
    # joined = tsne.reset_index().merge(dictionary, how='inner', on='id', sort=False).set_index('index')
    # cols = ['x', 'y', 'title']
    # joined.info()
    # joined = joined[cols]
    # joined.to_csv(finalPath, sep=' ', header=None, cols=cols, index=False)
