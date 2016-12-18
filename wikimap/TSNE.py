import logging
import numpy as np
from sklearn.manifold import TSNE

def train(embeddings):
    logger = logging.getLogger(__name__)

    logger.info('Constructing numpy array.')
    array = np.asarray(list(embeddings), dtype=np.float64)

    logger.info('Computing TSNE.')

    tsne = TSNE(n_components=2, n_iter=5000, verbose=1, method='barnes_hut', learning_rate=1000, perplexity=40, angle=0.8, early_exaggeration=4.0)

    return tsne.fit_transform(array)
