import logging
import word2vec


def Word2Vec(sentences, dimensions, context_size, epochs_count, dynamic_window,
             verbose):
    """Run word2vec on provided sentences."""
    logger = logging.getLogger(__name__)
    logger.info("Running word2vec...")

    w2v = word2vec.Word2Vec(dimension=dimensions, epochs=epochs_count,
                            context_size=context_size,
                            dynamic_context=dynamic_window, verbose=verbose)
    return w2v.learn_embeddings(sentences).iteritems()
