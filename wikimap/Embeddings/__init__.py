import embeddings
import logging

from embeddings import Embeddings, DEFAULT_DIMENSION, DEFAULT_EPOCH_COUNT,\
DEFAULT_CONTEXT_SIZE, DEFAULT_BACKTRACK_PROBABILITY, DEFAULT_WALKS_PER_NODE,\
DEFAULT_WALK_LENGTH, DEFAULT_DYNAMIC_WINDOW, DEFAULT_VERBOSE,\
DEFAULT_NEGATIVE_SAMPLES

EMBEDDING_METHODS = ['node2vec', 'bag_of_links', 'neighbor_list']
DEFAULT_EMBEDDING_METHOD = 'node2vec'
DEFAULT_EMBEDDING_NODE_COUNT = 1000000
DEFAULT_USE_CATEGORIES = 0

def Word2Vec(sentences, dimension, context_size, epoch_count, dynamic_window,
             negative_samples, verbose):
    """Run word2vec on provided sentences."""
    logger = logging.getLogger(__name__)
    logger.info("Running word2vec...")

    w2v = embeddings.Word2Vec(dimension=dimension, epochs=epoch_count,
                              context_size=context_size,
                              dynamic_context=dynamic_window,
                              negative_samples=negative_samples,
                              verbose=verbose)
    return w2v.train(sentences)


def Node2Vec(edges, backtrack_probability, walks_per_node, walk_length,
             dimension, context_size, epoch_count, dynamic_window,
             negative_samples, verbose):
    """Run node2vec on provided sentences."""
    logger = logging.getLogger(__name__)
    logger.info("Running node2vec...")

    n2v = embeddings.Node2Vec(backtrack_probability=backtrack_probability,
                              walk_length=walk_length,
                              walks_per_node=walks_per_node,
                              dimension=dimension, epochs=epoch_count,
                              context_size=context_size,
                              dynamic_context=dynamic_window,
                              negative_samples=negative_samples,
                              verbose=verbose)
    return n2v.train(edges)


class EmbeddingMethods(object):
    """Unified interface for running all types of word embedding algorithms."""

    def __init__(self,
                 method=DEFAULT_EMBEDDING_METHOD,
                 dimension=DEFAULT_DIMENSION,
                 epoch_count=DEFAULT_EPOCH_COUNT,
                 context_size=DEFAULT_CONTEXT_SIZE,
                 backtrack_probability=DEFAULT_BACKTRACK_PROBABILITY,
                 walks_per_node=DEFAULT_WALKS_PER_NODE,
                 walk_length=DEFAULT_WALK_LENGTH,
                 dynamic_window=DEFAULT_DYNAMIC_WINDOW,
                 negative_samples=DEFAULT_NEGATIVE_SAMPLES,
                 verbose=DEFAULT_VERBOSE):
        """
        Choose and validate the model.

        Some parameters may only be used in some models.

        `method` is the model type to use. Possible choices are:
        'node2vec', 'bag_of_links', 'neighbor_list'.

        `dimension` specifies the size of embeddings. It has to be a positive
        integer.

        `epoch_count` - number of training passes over the data

        `context_size` is the maximum context around the target word (this
        means that the size of the window around this word is
        2*context_size + 1).

        `backtrack_probability` is a probability of jumping back to the
        previous node when sampling random walks. Used by node2vec.

        `walks_per_node` is a number of random walks generated for each node
        in a graph used by node2vec.

        `walk_length` is a maximum length of a sampled path. Used in node2vec.

        `dynamic_window` controls whether the actual context_size is sampled
        with context_size being the max possible choice, or fixed to its value

        `negative_samples` controls the number of noise samples that are drawn
        for each real sample

        `verbose` - choose whether or not print additional info
        """
        if method in EMBEDDING_METHODS:
            self._method = method
        else:
            raise ValueError('`method` has to be one of available choices.')

        if isinstance(dimension, (int, long)) and dimension > 0:
            self._dimension = dimension
        else:
            raise ValueError(('`dimension` has to be a positive integer, is '
                              '{}.'.format(dimension)))

        if isinstance(context_size, (int, long)) and context_size > 0:
            self._context_size = context_size
        else:
            raise ValueError('`context_size` has to be a positive integer.')

        if (isinstance(backtrack_probability, float)
                and 0. <= backtrack_probability
                and backtrack_probability <= 1.):
            self._backtrack_probability = backtrack_probability
        else:
            raise ValueError('`backtrack_probability` has to be a float in \
                range of [0., 1.].')

        if isinstance(walks_per_node, (int, long)) and walks_per_node > 0:
            self._walks_per_node = walks_per_node
        else:
            raise ValueError('`walks_per_node` has to be a positive integer.')

        if isinstance(epoch_count, (int, long)) and epoch_count > 0:
            self._epoch_count = epoch_count
        else:
            raise ValueError('`epoch_count` has to be a positive integer.')

        if isinstance(walk_length, (int, long)) and walk_length > 0:
            self._walk_length = walk_length
        else:
            raise ValueError('`walk_length` has to be a positive integer.')

        if isinstance(negative_samples, (int, long)) and negative_samples > 0:
            self._negative_samples = negative_samples
        else:
            raise ValueError('`negative_samples` has to be a positive integer.')

        self._dynamic_window = dynamic_window
        self._verbose = verbose

    def train(self, data):
        """
        Run the specified embedding method.

        This method handles choosing and passing required arguments, depending
        on the selected embedding method.

        `data` is the data to train on.
        """
        if self._method == 'node2vec':
            return Node2Vec(
                data,
                backtrack_probability=self._backtrack_probability,
                walk_length=self._walk_length,
                walks_per_node=self._walks_per_node,
                dimension=self._dimension,
                epoch_count=self._epoch_count,
                context_size=self._context_size,
                dynamic_window=self._dynamic_window,
                negative_samples=self._negative_samples,
                verbose=self._verbose)
        elif self._method == 'bag_of_links':
            return Word2Vec(
                data,
                dimension=self._dimension,
                context_size=1,
                epoch_count=self._epoch_count,
                dynamic_window=False,
                negative_samples=self._negative_samples,
                verbose=self._verbose)
        elif self._method == 'neighbor_list':
            return Word2Vec(
                data,
                dimension=self._dimension,
                context_size=self._context_size,
                epoch_count=self._epoch_count,
                dynamic_window=False,
                negative_samples=self._negative_samples,
                verbose=self._verbose)
        else:
            raise ValueError('Unrecognized method.')
