import marisa_trie
import Utils

class Zoom(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class ZoomIndex(object):
    def __init__(self, indexPath):
        self._indexPath = indexPath
        self._index = marisa_trie.BytesTrie()

    def load(self):
        self._index.load(self._indexPath)
        return self

    def build(self, data):
        self._index = marisa_trie.BytesTrie([(idx, Utils.list2bytes(lst)) for idx, lst in data])
        self._index.save(self._indexPath)
        return self

    def get(self, zoom):
        zoomString = self._zoom2string(zoom)
        prefixes = [u''] + self._index.prefixes(zoomString)
        return Utils.bytes2list(self._index[prefixes[-1]][0])

    def _zoom2string(self, zoom):
        string = u''
        x, y, z = zoom.x, zoom.y, zoom.z

        while z > 0:
            mid = 2 ** (z - 1)
            if x < mid and y < mid:
                string += u'0'
            elif x >= mid and y < mid:
                string += u'1'
                x -= mid
            elif x >= mid and y >= mid:
                string += u'2'
                x -= mid
                y -= mid
            else:
                string += u'3'
                y -= mid

            z -= 1

        return string
