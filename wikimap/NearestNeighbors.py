import logging
import vptree

def computeNearestNeighbors(data, neighborsNo):
    logger = logging.getLogger(__name__)

    logger.info('Loading data.')
    data = list(data)

    logger.info('Creating vptree tree.')

    tree = vptree.VpTree(data)

    logger.info('Computing neighbors and distances.')
    batch = tree.getNearestNeighborsBatch(data, neighborsNo+1)
    distances = [dists[1:] for dists, _ in batch] # for every point its closest neighbor is the point itself, return only real neighbors
    indices = [inds[1:] for _, inds in batch] # for every point its closest neighbor is the point itself, return only real neighbors
    return distances, indices

