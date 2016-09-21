import gensim
import logging
import gc
import tsne
import numpy as np
import itertools as it
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def _loadVectors(modelPath, ids):
    logger = logging.getLogger(__name__)

    logger.info('Loading model.')
    model = gensim.models.Word2Vec.load(modelPath, mmap='r')

    logger.info('Getting vectors for {} words with highest pagerank score.'.format(len(ids)))

    vectors = np.asarray(model[ids], dtype=np.float64)

    model = None # release memory
    gc.collect() # release memory

    return vectors


def run(modelPath, selectedPages):
    logger = logging.getLogger(__name__)

    vectors = _loadVectors(modelPath, map(str, selectedPages))

    logger.info('Running PCA.')
    logger.info(vectors.shape)

    pca = PCA(50)
    vectors = pca.fit_transform(vectors)

    logger.info(vectors.shape)
    logger.info('Computing TSNE.')

    tsne = TSNE(n_components=2, n_iter=1000, verbose=1, method='barnes_hut')
    result = tsne.fit_transform(vectors)

    for i, (p, vec) in enumerate(zip(selectedPages, result)):
        yield (p, vec[0], vec[1], i)
