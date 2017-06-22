import graph


DEFAULT_AGGREGATION_DEPTH = 1


def pagerank(edges):
    return graph.pagerank(edges)

def aggregate(nodes, edges, depth=DEFAULT_AGGREGATION_DEPTH):
    return graph.aggregate(nodes, edges, depth)
