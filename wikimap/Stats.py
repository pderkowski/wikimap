import logging
import Utils

def countInOutDegrees(nodes, edges):
    logger = logging.getLogger(__name__)

    logger.info('Initializing counts.')

    nodes = frozenset(nodes)

    id2indeg = {}
    id2outdeg = {}

    for n in nodes:
        id2indeg[n] = 0
        id2outdeg[n] = 0

    logger.info('Iterating links.')

    for start, end in Utils.LogIt(10000000)(edges):
        if start in nodes and end in nodes:
            id2outdeg[start] += 1
            id2indeg[end] += 1

    for id_ in nodes:
        yield (id_, id2indeg[id_], id2outdeg[id_])

def countSmallNumbers(data, maxCounted=100):
    counts = [0] * (maxCounted + 1)

    for d in data:
        if d <= maxCounted:
            counts[d] += 1

    return counts
