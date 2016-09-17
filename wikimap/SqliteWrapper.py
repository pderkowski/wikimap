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
            cursor.execute("PRAGMA cache_size = 10000000")

            for i, line in enumerate(input):
                if i % 100 == 0:
                    logger.info("Processed {} records.".format(recordsTotal))

                if line.startswith(startPattern):
                    prepared = prepareLine(line)

                    # with timeit('Parsing. (C++)'):
                    records = self.blueprint['parser'](prepared, self.blueprint['namespaces'])

                    # with timeit('Unpacking, casting unicode. (Python)'):
                    # mapped = map(self.blueprint["unpackRecord"], records)

                    # with timeit('Inserting into the database. (Sqlite)'):
                    if records:
                        cursor.executemany("INSERT INTO "+self.blueprint["targetName"]+" VALUES "+self.blueprint["recordPattern"], records)

                        con.commit()

                        recordsTotal += len(records)

        logger.info("Finished loading the page table. Processed {} lines.".format(recordsTotal))

        for step in self.blueprint['postprocessing']:
            logger.info('Starting '+step+'...')
            con.execute(step)

pageTable = TableLoader({
    'sourceName': 'page',
    'targetName': 'page',
    'schema': (
            "DROP TABLE IF EXISTS page;\n"
            "CREATE TABLE page (\n"
            "page_id             INTEGER    NOT NULL                PRIMARY KEY,\n"
            "page_namespace      INTEGER    NOT NULL  DEFAULT '0',\n"
            "page_title          TEXT       NOT NULL  DEFAULT '');\n"),
    'recordPattern': '(?,?,?)',
    'parser': Tools.getPageRecords,
    'namespaces': [0, 14],
    'postprocessing': ['CREATE UNIQUE INDEX ns_title_idx ON page(page_namespace, page_title);']
})

linksTable = TableLoader({
    'sourceName': "pagelinks",
    'targetName': "links",
    'schema': (
            "DROP TABLE IF EXISTS links;\n"
            "CREATE TABLE links (\n"
            "pl_from             INTEGER    NOT NULL  DEFAULT '0',\n"
            "pl_namespace        INTEGER    NOT NULL  DEFAULT '0',\n"
            "pl_title            TEXT       NOT NULL  DEFAULT '',\n"
            "pl_from_namespace   INTEGER    NOT NULL  DEFAULT '0');\n"),
    'recordPattern': '(?,?,?,?)',
    'parser': Tools.getLinksRecords,
    'namespaces': [0, 14],
    'postprocessing': ["CREATE INDEX from_id_idx ON links(pl_from);",
        "CREATE INDEX ns_title_idx ON links(pl_namespace, pl_title);"]
})