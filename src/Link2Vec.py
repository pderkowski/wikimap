#!/usr/bin/env python

import os
import sys
import gensim
import argparse
import logging
import Utils
import Dictionary

dataPath = '../data'
modelPath = os.path.join(dataPath, 'model')

linksPath = os.path.join(dataPath, 'links')
dictionaryPath = os.path.join(dataPath, 'dictionary')

class LinkListsIterator(object):
    logger = logging.getLogger(__name__)

    # def __init__(self):

    #     self.dictionary = Dictionary.Dictionary()
    #     self.dictionary.load(dictionaryPath)

    def __iter__(self):
        with Utils.openOrExit(linksPath,'r') as links:
            for i, line in enumerate(links):
                if i % 100000 == 0:
                    logger.info('Processed {} lines'.format(i))
                # ids = [int(idStr) for idStr in line.rstrip().split()]
                # titles = [self.dictionary.id2title[id] for id in ids[1:]]
                # yield titles
                yield line.rstrip().split()

def link2vec():
    logger = logging.getLogger(__name__)

    logger.info('STARTED TRAINING')
    model = gensim.models.Word2Vec(LinkListsIterator(), sg=1,workers=4)
    model.save(modelPath)
    logger.info('FINISHED TRAINING')

def main():
    Utils.configLogging()
    link2vec()

if __name__ == '__main__':
    main()