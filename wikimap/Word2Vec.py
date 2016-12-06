import os
import sys
import gensim
import logging
import multiprocessing

def buildVocabulary(dataIterator, outputPath):
    model = gensim.models.Word2Vec(window=1, min_count=1, sample=0, sg=1, workers=multiprocessing.cpu_count(), batch_words=10000)
    model.build_vocab(dataIterator, progress_per=100000, custom_version=True)
    model.save(outputPath)

def train(dataIterator, vocabularyPath, outputPath):
    logger = logging.getLogger(__name__)

    logger.info('Loading vocabulary.')
    model = gensim.models.Word2Vec.load(vocabularyPath)
    logger.info(model)
    model.train(dataIterator, custom_version=True)
    logger.info(model)
    model.init_sims(replace=True)
    # model.delete_temporary_training_data(replace_word_vectors_with_normalized=True):
    model.save(outputPath)

def getEmbeddings(embeddingsPath, ids):
    model = gensim.models.Word2Vec.load(embeddingsPath, mmap='r')
    for id_ in ids:
        yield model[id_]

# def

# def iterateSimilar(modelPath):
#     logger = logging.getLogger(__name__)

#     logger.info('Loading model.')
#     model = gensim.models.Word2Vec.load(modelPath, mmap='r')

#     for i, word in enumerate(model.vocab):
#         if i % 100 == 0:
#             logger.info("Processed {} words.".format(i))
#         yield (word, model.similar_by_word(word))