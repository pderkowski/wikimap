import gensim
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import logging
import gc

def build(embeddings, output):
    logger = logging.getLogger(__name__)

    logger.info('Loading model.')
    model = gensim.models.Word2Vec.load(embeddings)

    vectorsNo = 100000
    logger.info('Getting vectors for {} most popular words.'.format(vectorsNo))
    ids = [model.index2word[i] for i in xrange(vectorsNo)]
    vectors = model[ids]

    model = None # release memory
    gc.collect() # release memory

    logger.info('Computing PCA.')
    pca = PCA(n_components=50)
    vectors = pca.fit_transform(vectors)

    logger.info('Computing TSNE.')
    tsne = TSNE(n_components=2, random_state=0, method='barnes_hut', verbose=1)
    with open(output,'w') as output:
        for id, vec in zip(ids, tsne.fit_transform(vectors)):
            output.write('{} {} {}\n'.format(id, vec[0], vec[1]))


# def plotTSNE(vectors, labels):
#     logger = logging.getLogger(__name__)

#     idx = np.arange(1, len(vectors) + 1)
#     sizes = np.log10(1.0 / idx)
#     sizes -= sizes[-1] - 1
#     sizes **= 2
#     sizes *= 5

#     plt.scatter(vectors[:, 0], vectors[:, 1], s=sizes)
#     plt.title("t-SNE, {} most popular words".format(vectors.shape[0]))
#     plt.axis('tight')
#     ax = plt.gca()
#     ax.xaxis.set_major_formatter(NullFormatter())
#     ax.yaxis.set_major_formatter(NullFormatter())

#     tooltip = tt.ToolTipOnHover(vectors, labels)
#     tooltip.attachTo(plt.gcf())

#     plt.show()

# def processAndPlot(n):
#     logger = logging.getLogger(__name__)

#     tsne, labels = tsneNMostPopular(n)
#     plotTSNE(tsne, labels)



