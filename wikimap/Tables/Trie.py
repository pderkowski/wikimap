import marisa_trie
import logging
from ..common.Utils import TrivialConverter

class Trie(object):
    def __init__(self, path, keyConverter=TrivialConverter(), valueConverter=TrivialConverter()):
        self._path = path
        self._keyC = keyConverter
        self._valC = valueConverter
        self._trie = None

    def create(self, data):
        logger = logging.getLogger(__name__)
        logger.info("Creating trie...")
        self._trie = marisa_trie.BytesTrie((self._keyC.encode(key), self._valC.encode(value)) for key, value in data)
        logger.info("Created trie with {} records".format(len(self._trie)))
        logger.info("Saving to {}".format(self._path))
        self._trie.save(self._path)

    def _ensureLoaded(self):
        if not self._trie:
            self._trie = marisa_trie.BytesTrie()
            self._trie.load(self._path)

    def prefixes(self, key):
        self._ensureLoaded()
        keyCode = self._keyC.encode(key)
        codes = self._trie.prefixes(keyCode)
        return map(self._keyC.decode, codes)

    def __getitem__(self, key):
        self._ensureLoaded()
        prefixes = self.prefixes(key)
        codes = map(self._keyC.encode, prefixes)
        return self._valC.decode(self._trie[codes[-1]][0])

    def __contains__(self, key):
        self._ensureLoaded()
        keyCode = self._keyC.encode(key)
        return keyCode in self._trie
