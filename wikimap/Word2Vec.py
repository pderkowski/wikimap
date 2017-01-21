import gensim
import logging
import multiprocessing
import sys

class Word2Vec(object):
    def __init__(self, path=None):
        self._path = path
        self._model = None

    def create(self, dataIterator):
        self._model = gensim.models.Word2Vec(window=1, min_count=1, sample=0, sg=1, workers=multiprocessing.cpu_count())
        self._model.build_vocab(dataIterator, progress_per=100000, custom_version=True)

    def save(self, path, trim=False):
        if trim:
            self._model.init_sims(replace=True)
            # model.delete_temporary_training_data(replace_word_vectors_with_normalized=True):

        self._model.save(path)

    def getEmbeddings(self, ids):
        self._ensureLoaded()

        for id_ in ids:
            yield self._model[id_]

    def getVocab(self):
        self._ensureLoaded()
        return list(self._model.vocab)

    def train(self, dataIterator, iterations=10):
        self._ensureLoaded()

        logger = logging.getLogger(__name__)

        self._model.iter = iterations
        self._model.batch_words = 10000
        logger.info(self._model)
        self._model.train(dataIterator, custom_version=True)
        logger.info(self._model)

    def _ensureLoaded(self):
        logger = logging.getLogger(__name__)

        if not self._model:
            if self._path:
                logger.info('Loading vocabulary.')
                self._model = gensim.models.Word2Vec.load(self._path)
            else:
                logger.critical('Trying to load the word2vec model, but no path specified.')
                sys.exit(1)
