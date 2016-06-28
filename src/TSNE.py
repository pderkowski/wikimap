#!/usr/bin/env python

import os
import sys
import gensim
import logging
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import ToolTipOnHover as tt
from sklearn.decomposition import PCA
import Utils

defaultModelPath = 'model'
defaultModel = None

def tsneNMostPopular(n):
    logger = logging.getLogger(__name__)

    global defaultModel
    if not defaultModel:
        defaultModel = gensim.models.Word2Vec.load(defaultModelPath)

    if not defaultModel.sorted_vocab:
        logging.info("Vocabulary unsorted, sorting it now.")
        defaultModel.sort_vocab()

    # take embeddings of n most frequent words
    labels = [defaultModel.index2word[i] for i in xrange(n)]
    embeddings = defaultModel[labels]

    pca = PCA(n_components=50)
    embeddings = pca.fit_transform(embeddings)

    logging.info('Got {} embeddings of dimension {}'.format(embeddings.shape[0], embeddings.shape[1]))
    tsne = TSNE(n_components=2, random_state=0)
    return tsne.fit_transform(embeddings), labels


def plotTSNE(vectors, labels):
    logger = logging.getLogger(__name__)

    idx = np.arange(1, len(vectors) + 1)
    sizes = np.log10(1.0 / idx)
    sizes -= sizes[-1] - 1
    sizes **= 2
    sizes *= 5

    plt.scatter(vectors[:, 0], vectors[:, 1], s=sizes)
    plt.title("t-SNE, {} most popular words".format(vectors.shape[0]))
    plt.axis('tight')
    ax = plt.gca()
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(NullFormatter())

    tooltip = tt.ToolTipOnHover(vectors, labels)
    tooltip.attachTo(plt.gcf())

    plt.show()

def processAndPlot(n):
    logger = logging.getLogger(__name__)

    tsne, labels = tsneNMostPopular(n)
    plotTSNE(tsne, labels)

def main():
    Uitls.configLogging()
    processAndPlot(1000)


if __name__ == '__main__':
    main()