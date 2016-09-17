import pandas as pd
import sqlite3
import logging

def test(pageTablePath, linksTablePath, output):
    con = sqlite3.connect(pageTablePath)
    con.execute('ATTACH DATABASE ? AS db2', (linksTablePath,))
    cursor = con.cursor()
    cursor.execute("""
        SELECT
            links.pl_from, page.page_id
        FROM
            page,
            db2.links AS links
        WHERE
            links.pl_namespace = page.page_namespace
        AND links.pl_title = page.page_title

        ORDER BY
            links.pl_from ASC""")

    logger = logging.getLogger(__name__)

    with open(output, 'w') as file:
        i = 0
        while True:
            records = cursor.fetchmany(size=10000)

            i += 10000

            logger.info(i)

            if records:
                for r in records:
                    file.write('{} {}'.format(r[0], r[1]))
            else:
                break
# def buildLinks(pageTablePath, linksTablePath, output):
#     con = sqlite3.connect(pageTablePath)
#     con.execute('ATTACH DATABASE ? AS db2', (linksTablePath,))
#     cursor = con.cursor()
#     cursor.execute('SELECT * FROM db2.links WHERE pl_from_namespace = ?, )
#     pp = pprint.PrettyPrinter()
#     pp.pprint(cursor.fetchall())

def buildFinalTable(tsnePath, dictionaryPath, finalPath):
    tsne = pd.read_table(tsnePath, delim_whitespace=True, header=None, names=['id', 'x', 'y'])
    dictionary = pd.read_table(dictionaryPath, delim_whitespace=True, header=None, names=['id', 'title'])
    joined = tsne.reset_index().merge(dictionary, how='inner', on='id', sort=False).set_index('index')
    cols = ['x', 'y', 'title']
    joined.info()
    joined = joined[cols]
    joined.to_csv(finalPath, sep=' ', header=None, cols=cols, index=False)
