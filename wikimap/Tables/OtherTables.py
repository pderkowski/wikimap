from ..common.Utils import IntConverter
from ..Embeddings import Embeddings
from Trie import Trie

class IndexedEmbeddingsTable(object):
    def __init__(self, embeddingsPath, indexPath):
        self._embeddings = Embeddings()
        self._embeddings.load(embeddingsPath)
        self._index = TitleIndex(indexPath)

    def __getitem__(self, title):
        return self._embeddings[self._index[title]]

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
