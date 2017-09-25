from edgearrayext import *
import logging
import collections

class EdgeArray(object):
    def __init__(self, path=None, log=True):
        self._path = path
        self._array = EdgeArrayExt()
        self._log = log

    def populate(self, iterator):
        logger = logging.getLogger(__name__)
        if self._log:
            logger.info("EdgeArray: populating...")

        self._array.populate(iter(iterator))
        if self._path:
            self._array.save(self._path)

    def append(self, edge):
        self._ensureLoaded()

        self._array.append(edge)

    def extend(self, edges):
        self._ensureLoaded()

        self._array.extend(edges)

    def sortByStartNode(self):
        self._ensureLoaded()

        logger = logging.getLogger(__name__)
        if self._log:
            logger.info('EdgeArray: sorting by start node...')

        self._array.sortByColumn(0)

    def sortByEndNode(self):
        self._ensureLoaded()

        logger = logging.getLogger(__name__)
        if self._log:
            logger.info('EdgeArray: sorting by end node...')

        self._array.sortByColumn(1)

    def filterByNodes(self, nodes):
        self._ensureLoaded()

        nodes = list(nodes)

        logger = logging.getLogger(__name__)
        if self._log:
            logger.info("EdgeArray: filtering by nodes (allowing {} nodes)...".format(len(nodes)))

        self._array.filterByNodes(nodes)

        if self._log:
            logger.info("EdgeArray: new size: {}".format(self._array.size()))

    def filterByStartNodes(self, nodes):
        self._ensureLoaded()

        nodes = list(nodes)

        logger = logging.getLogger(__name__)
        if self._log:
            logger.info("EdgeArray: filtering by start nodes (allowing {} nodes)...".format(len(nodes)))

        self._array.filterColumnByNodes(nodes, 0)

        if self._log:
            logger.info("EdgeArray: new size: {}".format(self._array.size()))

    def filterByEndNodes(self, nodes):
        self._ensureLoaded()

        nodes = list(nodes)

        logger = logging.getLogger(__name__)
        if self._log:
            logger.info("EdgeArray: filtering by end nodes (allowing {} nodes)...".format(len(nodes)))

        self._array.filterColumnByNodes(nodes, 1)

        if self._log:
            logger.info("EdgeArray: new size: {}".format(self._array.size()))

    def inverseEdges(self):
        self._ensureLoaded()

        logger = logging.getLogger(__name__)
        if self._log:
            logger.info("EdgeArray: inversing edges...")

        self._array.inverseEdges()

    def __iter__(self):
        self._ensureLoaded()
        for e in self._array:
            yield e

    def getStartNodes(self):
        self._ensureLoaded()

        return [s for (s, _) in self]

    def getEndNodes(self):
        self._ensureLoaded()

        return [e for (_, e) in self]

    def countNodes(self):
        self._ensureLoaded()

        logger = logging.getLogger(__name__)
        if self._log:
            logger.info("EdgeArray: counting nodes...")

        counts = collections.defaultdict(int)
        for (s, e) in self:
            counts[s] += 1
            counts[e] += 1
        return counts

    def _ensureLoaded(self):
        logger = logging.getLogger(__name__)

        if self._array.size() == 0 and self._path:
            if self._log:
                logger.info("EdgeArray: loading...")
            self._array.load(self._path)

            if self._log:
                logger.info("EdgeArray: new size: {}".format(self._array.size()))
