from ..common.CDBStore import CDBStore
from ..common.Utils import IntConverter, FloatConverter, ListConverter
from Trie import Trie

class EmbeddingsTable(object):
    def __init__(self, path):
        self._db = CDBStore(path, IntConverter(), ListConverter(FloatConverter()))

    def create(self, data):
        self._db.create(data)

    def get(self, key):
        return self._db.get(key)

    def keys(self):
        return self._db.keys()

class IndexedEmbeddingsTable(object):
    def __init__(self, embeddingsPath, indexPath):
        self._db = CDBStore(embeddingsPath, IntConverter(), ListConverter(FloatConverter()))
        self._index = TitleIndex(indexPath)

    def __getitem__(self, title):
        return self._db.get(self._index[title])

    def __contains__(self, title):
        return title in self._index

class TitleIndex(object):
    def __init__(self, path):
        self._trie = Trie(path, IntConverter())

    def create(self, data):
        self._trie.create(data)

    def __getitem__(self, title):
        return self._trie[title]

    def __contains__(self, title):
        return title in self._trie
