from CDBStore import CDBStore
from Utils import IntConverter, ListConverter

class AggregatedLinksTable(object):
    def __init__(self, path):
        self._db = CDBStore(path, IntConverter(), ListConverter(IntConverter()))

    def create(self, data):
        self._db.create(data)

    def get(self, key):
        return self._db.get(key)
