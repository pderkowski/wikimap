import cdb
import logging
import struct

def loadCDBStore(path):
    return cdb.init(path)

class TrivialConverter(object):
    def encode(self, value):
        return str(value)

    def decode(self, value):
        return value

class IntConverter(object):
    def __init__(self):
        self.size = 4

    def encode(self, value):
        return struct.pack("<i", value)

    def decode(self, string):
        return struct.unpack("<i", string)[0]

class FloatConverter(object):
    def __init__(self):
        self.size = 8

    def encode(self, value):
        return struct.pack("<d", value)

    def decode(self, string):
        return struct.unpack("<d", string)[0]

class ListConverter(object):
    def __init__(self, converter):
        self._converter = converter

    def encode(self, lst):
        bytes_ = ''.join(map(self._converter.encode, lst))
        return str(bytes_)

    def decode(self, string):
        codes = [string[i:i+self._converter.size] for i in range(0, len(string), self._converter.size)]
        return map(self._converter.decode, codes)

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

        logger.info("Added {} records to CDB {}.".format(maker.numentries, maker.fn))

        maker.finish()
        del maker

    def get(self, key, pos=0):
        self._ensureLoaded()
        try:
            return self._valueConverter.decode(self._db.get(self._keyConverter.encode(key), pos))
        except struct.error:
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
