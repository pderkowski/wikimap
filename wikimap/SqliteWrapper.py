import gzip
import os
import sqlite3
import logging
import Tools
import sys
import re
import Utils

import time
from contextlib import contextmanager

@contextmanager
def timeit(name):
    startTime = time.time()
    yield
    elapsedTime = time.time() - startTime
    print('[{}] finished in {} ms'.format(name, int(elapsedTime * 1e3)))


class TableLoader(object):
    def __init__(self, blueprint):
        self.blueprint = blueprint

    def _createTable(self, path):
        con = sqlite3.connect(path)

        con.executescript(self.blueprint["schema"])
        con.commit()

        return con

    def loadTable(self, inputPath, outputPath):
        startPattern = 'INSERT INTO `'+self.blueprint["sourceName"]+'` VALUES '

        def prepareLine(line):
            return line.rstrip()[len(startPattern):-1] # line ends with ;

        logger = logging.getLogger(__name__)
        logger.info("Starting loading the {} table.".format(self.blueprint["targetName"]))

        recordsTotal = 0
        with gzip.GzipFile(inputPath,'r') as input, self._createTable(outputPath) as con:
            cursor = con.cursor()
            cursor.execute("PRAGMA synchronous = OFF")
            cursor.execute("PRAGMA journal_mode = OFF")

            for i, line in enumerate(input):
                if i % 100 == 0:
                    logger.info("Processed {} records.".format(recordsTotal))

                if line.startswith(startPattern):
                    # print

                    prepared = prepareLine(line)

                    # with timeit('Parsing. (C++)'):
                    records = self.blueprint['parser'](prepared)

                    # with timeit('Unpacking, casting unicode. (Python)'):
                    mapped = map(self.blueprint["unpackRecord"], records)

                    # with timeit('Inserting into the database. (Sqlite)'):
                    cursor.executemany("INSERT INTO "+self.blueprint["targetName"]+" VALUES "+self.blueprint["recordPattern"], mapped)

                    con.commit()

                    recordsTotal += len(records)

        logger.info("Finished loading the page table. Processed {} lines.".format(recordsTotal))

        if 'postprocessing' in self.blueprint:
            logger.info('Starting postprocessing...')
            con.executescript(self.blueprint['postprocessing'])
            logger.info('Finished postprocessing.')

def fixDecode(string):
    try:
        return unicode(string, encoding='utf8')
    except UnicodeDecodeError:
        logging.warn(u'Invalid utf8 encoding for: '+unicode(string, encoding='utf8', errors='replace')+u', falling back to cp1252.')

        try:
            decoded = unicode(string, encoding='cp1252')
            logging.warn(u'Succesfully decoded a string: '+decoded+' as cp1252.')
            return decoded
        except UnicodeDecodeError:
            logging.error(u'Invalid cp1252 encoding for: '+unicode(string, encoding='cp1252', errors='replace')+u', returning the incomplete utf8 version.')
            return unicode(string, encoding='utf8', errors='ignore')

pageTable = TableLoader({
    'sourceName': 'page',
    'targetName': 'page',
    'schema': (
            "DROP TABLE IF EXISTS page;\n"
            "CREATE TABLE page (\n"
            "page_id             INTEGER         NOT NULL                PRIMARY KEY,\n"
            "page_namespace      INTEGER         NOT NULL  DEFAULT '0',\n"
            "page_title          TEXT            NOT NULL  DEFAULT ''\n"
            ");\n"),
    'unpackRecord': lambda r: (r.id, r.ns, fixDecode(r.title)),
    'recordPattern': '(?,?,?)',
    'parser': Tools.parsePageValues
})

linksTable = TableLoader({
    'sourceName': "pagelinks",
    'targetName': "links",
    'schema': (
            "DROP TABLE IF EXISTS links;\n"
            "CREATE TABLE links (\n"
            "pl_from             INTEGER         NOT NULL  DEFAULT '0',\n"
            "pl_namespace        INTEGER         NOT NULL  DEFAULT '0',\n"
            "pl_title            TEXT            NOT NULL  DEFAULT '',\n"
            "pl_from_namespace   INTEGER         NOT NULL  DEFAULT '0');\n"),
    'unpackRecord': lambda r: (r.from_, r.ns, fixDecode(r.title), r.from_ns),
    'recordPattern': '(?,?,?,?)',
    'parser': Tools.parseLinksValues,
    'postprocessing': "CREATE INDEX pl_from_ids ON links(pl_from);"
})