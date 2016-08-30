import gensim
import logging
import gc
import tsne
import numpy as np

def _loadVectors(file, vectorsNo):
    logger = logging.getLogger(__name__)

    logger.info('Loading model.')
    model = gensim.models.Word2Vec.load(file)

    if vectorsNo < 0:
        ids = list(model.index2word)
    else:
        ids = [model.index2word[i] for i in xrange(vectorsNo)]

    logger.info('Getting vectors for {} most popular words.'.format(len(ids)))

    vectors = np.asarray(model[ids], dtype=np.float64)

    model = None # release memory
    gc.collect() # release memory

    return ids, vectors


def run(input, output):
    logger = logging.getLogger(__name__)

    ids, vectors = _loadVectors(input, 1000000) # negative = load all

    logger.info('Computing TSNE.')
    result = tsne.bh_sne(vectors, pca_d=50)

    with open(output,'w') as output:
        for id, vec in zip(ids, result):
            output.write('{} {} {}\n'.format(id, vec[0], vec[1]))
