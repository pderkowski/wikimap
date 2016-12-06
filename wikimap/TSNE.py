import logging
import gc
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
# from MulticoreTSNE import MulticoreTSNE as TSNE
import multiprocessing


# def _loadVectors(modelPath, ids):
#     logger = logging.getLogger(__name__)

#     logger.info('Loading model.')
#     model = gensim.models.Word2Vec.load(modelPath, mmap='r')

#     logger.info('Getting vectors for {} words with highest pagerank score.'.format(len(ids)))

#     vectors = np.asarray(model[ids], dtype=np.float64)

#     model = None # release memory
#     gc.collect() # release memory

#     return vectors


def train(embeddings):
    logger = logging.getLogger(__name__)

    logger.info('Constructing numpy array.')
    array = np.asarray(list(embeddings), dtype=np.float64)

    # logger.info('Running PCA.')
    # pca = PCA(50)
    # array = pca.fit_transform(array)
    # pca = None # release memory
    # gc.collect() # release memory

    logger.info('Computing TSNE.')

    # tsne = TSNE(n_components=2, n_iter=5000, verbose=1, method='barnes_hut', learning_rate=200, perplexity=20, n_jobs=multiprocessing.cpu_count())
    tsne = TSNE(n_components=2, n_iter=5000, verbose=1, method='barnes_hut', learning_rate=1000, perplexity=40, angle=0.8, early_exaggeration=4.0)

    result = tsne.fit_transform(array)

    return result