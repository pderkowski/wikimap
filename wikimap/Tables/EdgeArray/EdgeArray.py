from edgearrayext import *
import logging

class EdgeArray(object):
    def __init__(self, path, shuffle=False, log=True, stringify=False):
        self._path = path
        self._array = EdgeArrayExt()
        self._shuffle = shuffle
        self._log = log
        self._stringify = stringify

    def populate(self, iterator):
        logger = logging.getLogger(__name__)
        if self._log:
            logger.info("EdgeArray: populating...")

        self._array.populate(iter(iterator))
        self._array.save(self._path)

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

        logger = logging.getLogger(__name__)
        if self._shuffle:
            if self._log:
                logger.info("EdgeArray: shuffling...")
            self._array.shuffle()

        if self._stringify:
            return self._array.iterStrings()
        else:
            return iter(self._array)

    def _ensureLoaded(self):
        logger = logging.getLogger(__name__)

        if self._array.size() == 0:
            if self._log:
                logger.info("EdgeArray: loading...")
            self._array.load(self._path)

            if self._log:
                logger.info("EdgeArray: new size: {}".format(self._array.size()))
