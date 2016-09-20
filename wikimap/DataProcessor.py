import pandas as pd
import sqlite3
import logging
import pprint
import codecs
import SqliteWrapper
import Utils
import Pagerank
import Link2Vec

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
            pl_from"""


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
            pr_id             INTEGER    NOT NULL   UNIQUE,
            pr_rank           REAL       NOT NULL
        );""")

    prCon.executemany("INSERT INTO pagerank VALUES (?, ?)", Pagerank.pagerank(selection))
    prCon.commit()

def buildFinalTable(tsnePath, dictionaryPath, finalPath):
    tsne = pd.read_table(tsnePath, delim_whitespace=True, header=None, names=['id', 'x', 'y'])
    dictionary = pd.read_table(dictionaryPath, delim_whitespace=True, header=None, names=['id', 'title'])
    joined = tsne.reset_index().merge(dictionary, how='inner', on='id', sort=False).set_index('index')
    cols = ['x', 'y', 'title']
    joined.info()
    joined = joined[cols]
    joined.to_csv(finalPath, sep=' ', header=None, cols=cols, index=False)
