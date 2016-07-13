import gensim
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

def build(embeddings, output):
    model = gensim.models.Word2Vec.load(embeddings)

    ids = [model.index2word[i] for i in xrange(1000)]
    vectors = model[ids]

    pca = PCA(n_components=50)
    vectors = pca.fit_transform(vectors)

    tsne = TSNE(n_components=2, random_state=0, method='barnes_hut')
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



