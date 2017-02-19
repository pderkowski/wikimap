from ..common.CDBStore import CDBStore, IntConverter, FloatConverter, ListConverter

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
