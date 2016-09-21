import os
import sys
import gensim
import logging
import Utils
import multiprocessing

def build(linksIterator, output):
    logger = logging.getLogger(__name__)

    logger.info('STARTED TRAINING')
    model = gensim.models.Word2Vec(linksIterator, min_count=1, sg=1, workers=multiprocessing.cpu_count())
    logger.info(model)
    model.save(output)
    logger.info('FINISHED TRAINING')

