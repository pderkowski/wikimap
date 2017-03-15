from scipy import stats, linalg
from numpy import dot, array
import logging

def normalize(vec):
    return array(vec) / linalg.norm(vec)

class Evaluator(object):
    def __init__(self, embeddings, word_mapping):
        self._embeddings = embeddings
        self._word_mapping = word_mapping
        self._logger = logging.getLogger(__name__)

    def _get_embedding(self, word):
        return self._embeddings[self._maybe_map(word)]

    def _maybe_map(self, word):
        if word in self._word_mapping:
            return self._word_mapping[word]
        else:
            return word

class SimilarityEvaluator(Evaluator):
    def __init__(self, embeddings, word_mapping):
        super(SimilarityEvaluator, self).__init__(embeddings, word_mapping)

    def evaluate(self, dataset):
        self._logger.info('Evaluating {} ({})...'.format(dataset.name, dataset.type))

        true_scores, my_scores = [], []
        matched_examples, skipped_examples = 0, 0
        for (example, true_score) in dataset:
            try:
                my_scores.append(self._score(example))
                true_scores.append(true_score)
                matched_examples += 1
            except KeyError:
                skipped_examples += 1

        spearman_rho = stats.stats.spearmanr(my_scores, true_scores)[0]
        self._logger.info('{} score: {}, matched: {}, skipped: {}'.format(dataset.name, spearman_rho, matched_examples, skipped_examples))
        return { 'name': dataset.name, 'type': dataset.type, 'method': 'spearman', 'score': spearman_rho, 'matched_examples': matched_examples, 'skipped_examples': skipped_examples }

    def _score(self, example):
        w1, w2 = example
        vec1, vec2 = self._get_embedding(w1), self._get_embedding(w2)
        return dot(vec1, vec2) / (linalg.norm(vec1) * linalg.norm(vec2))

class RelationEvaluator(Evaluator):
    def __init__(self, embeddings, word_mapping):
        super(RelationEvaluator, self).__init__(embeddings, word_mapping)

    def evaluate(self, dataset):
        self._logger.info('Evaluating {} ({})...'.format(dataset.name, dataset.type))

        matched_examples, skipped_examples = 0, 0
        correct, incorrect = 0, 0
        for example in dataset:
            try:
                is_correct = self._score(example)
                correct += 1 if is_correct else 0
                incorrect += 0 if is_correct else 1
                matched_examples += 1
            except KeyError:
                skipped_examples += 1

        fraction = float(correct) / (correct + incorrect)
        self._logger.info('{} score: {}, matched: {}, skipped: {}'.format(dataset.name, fraction, matched_examples, skipped_examples))
        return { 'name': dataset.name, 'type': dataset.type, 'method': 'fraction', 'score': fraction, 'matched_examples': matched_examples, 'skipped_examples': skipped_examples }

    def _score(self, example):
        word, positive, negative = example
        vec_word, vec_pos, vec_neg = self._get_embedding(word), self._get_embedding(positive), self._get_embedding(negative)
        vec_word = normalize(vec_word)
        vec_pos = normalize(vec_pos)
        vec_neg = normalize(vec_neg)
        return dot(vec_word, vec_pos) > dot(vec_word, vec_neg)
