from whoosh.fields import Schema, NGRAMWORDS, STORED
from whoosh.qparser import SimpleParser
import whoosh
import urllib
import os
import multiprocessing

class Term(object):
    def __init__(self, term, isCategory):
        self.term = term.replace('_', ' ')
        self.isCategory = isCategory

class TermIndex(object):
    def __init__(self, idxPath):
        self._idxPath = idxPath
        self._index = None

        self._schema = Schema(term=NGRAMWORDS(minsize=2, maxsize=4, stored=True), isCategory=STORED)
        self._parser = SimpleParser('term', self._schema)

        if self._exists():
            self._load()
        else:
            self._create()

    def add(self, data):
        with self._index.writer(procs=multiprocessing.cpu_count(), limitmb=1024, multisegment=True) as writer:
            for r in data:
                writer.add_document(term=r[0], isCategory=r[1])

    def search(self, term, limit):
        query = self._parser.parse(urllib.unquote(term))
        with self._index.searcher() as searcher:
            results = searcher.search(query, limit=limit)
            return [Term(r['term'], r['isCategory']) for r in results]

    def isEmpty(self):
        return self._index.doc_count() == 0

    def _exists(self):
        return whoosh.index.exists_in(self._idxPath)

    def _create(self):
        print 'Creating index {}'.format(self._idxPath)
        os.makedirs(self._idxPath)
        self._index = whoosh.index.create_in(self._idxPath, self._schema)

    def _load(self):
        print 'Loading index {}'.format(self._idxPath)
        self._index = whoosh.index.open_dir(self._idxPath)
