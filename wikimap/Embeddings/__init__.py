import Node2Vec


class Embeddings(object):
    """Unified interface for running all types of word embedding algorithms."""

    def __init__(self, method='node2vec', dimensions=128, epochs_count=1,
                 context_size=10, backtrack_probability=0.5, walks_per_node=10,
                 walk_length=80, dynamic_window=True, verbose=True):
        """
        Choose and validate the model.

        Some parameters may only be used in some models.

        `method` is the model type to use. Possible choices are: 'node2vec'.

        `dimensions` specifies the size of embeddings. It has to be a positive
        integer.

        `epochs_count` - number of training passes over the data

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

        `verbose` - choose whether or not print additional info
        """
        if method in ['node2vec']:
            self._method = method
        else:
            raise ValueError('`method` has to be one of available choices.')

        if isinstance(dimensions, int) and dimensions > 0:
            self._dimensions = dimensions
        else:
            raise ValueError('`dimensions` has to be a positive integer.')

        if isinstance(context_size, int) and context_size > 0:
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

        if isinstance(walks_per_node, int) and walks_per_node > 0:
            self._walks_per_node = walks_per_node
        else:
            raise ValueError('`walks_per_node` has to be a positive integer.')

        if isinstance(epochs_count, int) and epochs_count > 0:
            self._epochs_count = epochs_count
        else:
            raise ValueError('`epochs_count` has to be a positive integer.')

        if isinstance(walk_length, int) and walk_length > 0:
            self._walk_length = walk_length
        else:
            raise ValueError('`walk_length` has to be a positive integer.')

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
            return iter(Node2Vec.Node2Vec(
                data,
                self._dimensions,
                self._context_size,
                self._backtrack_probability,
                self._walks_per_node,
                self._walk_length,
                self._epochs_count,
                self._dynamic_window,
                self._verbose))
        else:
            raise ValueError('Unrecognized method.')
