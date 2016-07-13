import os
import sys
import gensim
import logging
import Utils

class LinkListsIterator(object):
    logger = logging.getLogger(__name__)

    def __init__(self, aggregatedLinks):
        self.aggregatedLinks = aggregatedLinks

    def __iter__(self):
        with Utils.openOrExit(self.aggregatedLinks,'r') as links:
            for i, line in enumerate(links):
                if i % 100000 == 0:
                    logger.info('Processed {} lines'.format(i))
                # ids = [int(idStr) for idStr in line.rstrip().split()]
                # titles = [self.dictionary.id2title[id] for id in ids[1:]]
                # yield titles
                yield line.rstrip().split()

def build(aggregatedLinks, output):
    logger = logging.getLogger(__name__)

    logger.info('STARTED TRAINING')
    model = gensim.models.Word2Vec(LinkListsIterator(aggregatedLinks), sg=1, workers=4)
    model.save(output)
    logger.info('FINISHED TRAINING')

