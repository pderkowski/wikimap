from ..common.CDBStore import CDBStore
from ..common.Utils import IntConverter, FloatConverter, ListConverter
from Trie import Trie

class AggregatedLinksTable(object):
    def __init__(self, path):
        self._db = CDBStore(path, IntConverter(), ListConverter(IntConverter()))

    def create(self, data):
        self._db.create(data)

    def get(self, key):
        return self._db.get(key)

class EmbeddingsTable(object):
    def __init__(self, path):
        self._db = CDBStore(path, IntConverter(), ListConverter(FloatConverter()))

    def create(self, data):
        self._db.create(data)

    def get(self, key):
        return self._db.get(key)

    def keys(self):
        return self._db.keys()

class EmbeddingIndex(object):
    def __init__(self, path):
        self._idx = Trie(path, IntConverter())

    def create(self, data):
        self._idx.create(data)
