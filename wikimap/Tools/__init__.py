from libsqltools import *
import gzip

class TableImporter(object):
    def __init__(self, path, parser, tableName):
        self._path = path
        self._parser = parser
        self._tableName = tableName

    def read(self):
        with gzip.GzipFile(self._path, 'r') as input:
            for line in input:
                pattern = 'INSERT INTO `{}` VALUES '.format(self._tableName)
                if line.startswith(pattern):
                    for r in self._parser(line.rstrip()[len(pattern):-1]): # line ends with ;
                        yield r
