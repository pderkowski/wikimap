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

class NormalizingConverter(object):
    def encode(self, word):
        return word.lower().replace(u' ', u'_')

    def decode(self, code):
        return code.replace(u'_', u' ')

class EmbeddingIndex(object):
    def __init__(self, path):
        self._trie = Trie(path, NormalizingConverter(), IntConverter())

    def create(self, data):
        self._trie.create(data)

    def get(self, key):
        return self._trie[key]

    def has(self, key):
        return key in self._trie

class IndexedEmbeddingsTable(object):
    def __init__(self, embeddingsPath, indexPath):
        self._db = CDBStore(embeddingsPath, IntConverter(), ListConverter(FloatConverter()))
        self._index = EmbeddingIndex(indexPath)

    def get(self, key):
        return self._db.get(self._index.get(key))

    def has(self, key):
        return self._index.has(key)
