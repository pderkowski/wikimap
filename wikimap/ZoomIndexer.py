from math import floor, ceil
import logging

class Indexer(object):
    def __init__(self, points, data, bucketSize):
        logger = logging.getLogger(__name__)

        self._bucketSize = bucketSize
        self._idx2bucket = {u'': []}
        self._data2index = {}

        points = list(points)
        data = list(data)

        self._bounds = self._findBounds(points)
        logger.info('Bounds: ({}, {}) -- ({}, {})'.format(*self._bounds))

        for p, d in zip(points, data):
            self._add(p, d)

        self._prune()

    def getBounds(self):
        return self._bounds

    def index2data(self):
        return [(idx, [d for _, d in lst]) for idx, lst in self._idx2bucket.iteritems()]

    def data2index(self):
        return self._data2index.iteritems()

    def _add(self, point, data):
        bucketIdx = self._findBucket(point)

        if self._isFull(bucketIdx):
            self._split(bucketIdx)
            bucketIdx = self._findBucket(point)

        self._idx2bucket[bucketIdx].append((point, data))

        if data not in self._data2index:
            self._data2index[data] = bucketIdx

    def _isFull(self, idx):
        return len(self._idx2bucket[idx]) >= self._bucketSize

    def _findBucket(self, point):
        idx = u''
        bounds = self._bounds

        while True:
            extendedIdx, extendedBounds = self._extend(idx, bounds, point)
            if extendedIdx in self._idx2bucket:
                idx, bounds = extendedIdx, extendedBounds
            else:
                break

        return idx

    def _extend(self, idx, bounds, point):
        xmin, ymin, xmax, ymax = bounds
        xmid, ymid = (xmin + xmax) / 2, (ymin + ymax) / 2

        if   point[0] >= xmin and point[0] < xmid \
        and  point[1] >= ymin and point[1] < ymid:
            return idx+u'0', (xmin, ymin, xmid, ymid)
        elif point[0] >= xmid and point[0] < xmax \
        and  point[1] >= ymin and point[1] < ymid:
            return idx+u'1', (xmid, ymin, xmax, ymid)
        elif point[0] >= xmid and point[0] < xmax \
        and  point[1] >= ymid and point[1] < ymax:
            return idx+u'2', (xmid, ymid, xmax, ymax)
        elif point[0] >= xmin and point[0] < xmid \
        and  point[1] >= ymid and point[1] < ymax:
            return idx+u'3', (xmin, ymid, xmid, ymax)
        else:
            raise RuntimeError('Point is not in bounds.')

    def _split(self, idx):
        self._idx2bucket[idx+u'0'] = []
        self._idx2bucket[idx+u'1'] = []
        self._idx2bucket[idx+u'2'] = []
        self._idx2bucket[idx+u'3'] = []

        for p, d in self._idx2bucket[idx]:
            self._add(p, d)

    def _findBounds(self, points):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return floor(min(xs)), floor(min(ys)), ceil(max(xs)), ceil(max(ys))

    def _prune(self):
        doomed = [index for index, datalist in self._idx2bucket.iteritems() if len(datalist) == 0]
        for index in doomed:
            del self._idx2bucket[index]
