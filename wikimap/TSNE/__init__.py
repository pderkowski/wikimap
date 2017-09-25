import logging
import numpy as np
import bhtsne

DEFAULT_POINT_COUNT = 100000

def train(embeddings):
    logger = logging.getLogger(__name__)

    logger.info('Constructing numpy array.')
    array = np.asarray(list(embeddings), dtype=np.float64)

    logger.info('Computing TSNE.')

    return bhtsne.run_bh_tsne(array, no_dims=2, perplexity=40, theta=0.5, randseed=-1, verbose=True, initial_dims=50)
