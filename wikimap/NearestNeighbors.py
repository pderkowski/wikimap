from sklearn.neighbors import NearestNeighbors
import logging
import Utils

def computeNearestNeighbors(data, neighborsNo):
    logger = logging.getLogger(__name__)

    logger.info('Loading data.')
    data = Utils.any2array(data)

    logger.info('Creating ball tree.')
    nbrs = NearestNeighbors(n_neighbors=neighborsNo+1, algorithm='ball_tree', metric='euclidean').fit(data) # +1, because the closest point is the point itself

    logger.info('Computing neighbors and distances.')
    distances, indices = nbrs.kneighbors(data)

    return distances[:, 1:], indices[:, 1:] # for every point its closest neighbor is the point itself, return only real neighbors

