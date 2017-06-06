import cdb
import logging
import struct
from Utils import TrivialConverter

def loadCDBStore(path):
    return cdb.init(path)

class CDBStore(object):
    def __init__(self, path, keyConverter=TrivialConverter(), valueConverter=TrivialConverter()):
        self._path = path
        self._keyConverter = keyConverter
        self._valueConverter = valueConverter
        self._db = None

    def create(self, data):
        logger = logging.getLogger(__name__)

        maker = cdb.cdbmake(self._path, self._path + ".tmp")

        logger.info("Creating {}.".format(maker.fn))

        for key, value in data:
            maker.add(self._keyConverter.encode(key), self._valueConverter.encode(value))

        logger.info("Created {} with {} records".format(maker.fn, maker.numentries))

        maker.finish()
        del maker

    def get(self, key, pos=0):
        self._ensureLoaded()
        try:
            return self._valueConverter.decode(self._db.get(self._keyConverter.encode(key), pos))
        except:
            raise KeyError(key)

    def getall(self, key):
        self._ensureLoaded()
        return map(self._valueConverter.decode, self._db.getall(self._keyConverter.encode(key)))

    def __getitem__(self, key):
        return self.get(key, 0)

    def __contains__(self, key):
        self._ensureLoaded()
        return self._db.has_key(key)

    def _ensureLoaded(self):
        if not self._db:
            self._db = cdb.init(self._path)

    def keys(self):
        self._ensureLoaded()
        return map(self._keyConverter.decode, self._db.keys())
