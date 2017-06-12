from scipy import stats, linalg
from numpy import dot, array
import logging


def normalize(vec):
    return array(vec) / linalg.norm(vec)


class SimilarityEvaluator(object):
    def __init__(self, embeddings):
        self._embeddings = embeddings
        self._logger = logging.getLogger(__name__)

    def evaluate(self, dataset):
        self._logger.info('Evaluating {} ({})...'.format(dataset.name,
                                                         dataset.type))

        true_scores, my_scores = [], []
        matched, skipped = 0, 0
        for (id1, id2, true_score) in dataset:
            try:
                my_scores.append(self._score(id1, id2))
                true_scores.append(true_score)
                matched += 1
            except KeyError:
                skipped += 1

        spearman_rho = stats.stats.spearmanr(my_scores, true_scores)[0]

        self._logger.info('{} score: {}, matched: {}, skipped: {}'.format(
            dataset.name, spearman_rho, matched, skipped))

        return {
            'name': dataset.name,
            'type': dataset.type,
            'method': 'spearman',
            'score': spearman_rho,
            'matched_examples': matched,
            'skipped_examples': skipped
        }

    def _score(self, id1, id2):
        vec1, vec2 = self._embeddings.get(id1), self._embeddings.get(id2)
        return dot(vec1, vec2) / (linalg.norm(vec1) * linalg.norm(vec2))


class TripletEvaluator(object):
    def __init__(self, embeddings):
        self._embeddings = embeddings
        self._logger = logging.getLogger(__name__)

    def evaluate(self, dataset):
        self._logger.info('Evaluating {} ({})...'.format(dataset.name,
                                                         dataset.type))

        correct, incorrect = 0, 0
        matched, skipped = 0, 0
        for id1, id2, id3 in dataset:
            try:
                is_correct = self._score(id1, id2, id3)
                correct += 1 if is_correct else 0
                incorrect += 0 if is_correct else 1
                matched += 1
            except KeyError:
                skipped += 1

        if correct == 0 and incorrect == 0:
            fraction = 0.
        else:
            fraction = float(correct) / (correct + incorrect)

        self._logger.info('{} score: {}, matched: {}, skipped: {}'.format(
            dataset.name, fraction, matched, skipped))

        return {
            'name': dataset.name,
            'type': dataset.type,
            'method': 'fraction',
            'score': fraction,
            'matched_examples': matched,
            'skipped_examples': skipped
        }

    def _score(self, id1, id2, id3):
        vec_word = normalize(self._embeddings.get(id1))
        vec_pos = normalize(self._embeddings.get(id2))
        vec_neg = normalize(self._embeddings.get(id3))

        return dot(vec_word, vec_pos) > dot(vec_word, vec_neg)
