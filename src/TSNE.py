import gensim
import logging
import gc
import tsne
import numpy as np
import itertools as it

def _iterPagerank(pagerankPath):
    with open(pagerankPath, 'r') as pagerank:
        for line in pagerank:
            yield line.split()[0]

def _loadVectors(modelPath, pagerankPath, vectorsNo):
    logger = logging.getLogger(__name__)

    logger.info('Loading model.')
    model = gensim.models.Word2Vec.load(modelPath)

    ids = list(it.islice(_iterPagerank(pagerankPath), vectorsNo))

    logger.info('Getting vectors for {} words with highest pagerank score.'.format(len(ids)))

    vectors = np.asarray(model[ids], dtype=np.float64)

    model = None # release memory
    gc.collect() # release memory

    return ids, vectors


def run(modelPath, pagerankPath, output):
    logger = logging.getLogger(__name__)

    ids, vectors = _loadVectors(modelPath, pagerankPath, 5000) # if last value is None = load all

    logger.info('Computing TSNE.')
    result = tsne.bh_sne(vectors, pca_d=50)

    with open(output,'w') as output:
        for id, vec in zip(ids, result):
            output.write('{} {} {}\n'.format(id, vec[0], vec[1]))
