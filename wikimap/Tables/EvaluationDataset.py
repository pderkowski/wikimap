from ..DataHelpers import normalize_word
from scipy import stats, linalg
from numpy import dot
import logging
import csv

class WordMapping(object):
    def __init__(self, path):
        self._mapping = self._read_mapping(path)

    def __getitem__(self, key):
        return self._mapping[key]

    def __contains__(self, key):
        return key in self._mapping

    def __len__(self):
        return len(self._mapping)

    def __iter__(self):
        return iter(self._mapping)

    def iteritems(self):
        return self._mapping.iteritems()

    @staticmethod
    def _read_mapping(path):
        mapping = {}
        with open(path, 'r') as infile:
            for line in infile:
                what, to = line.rstrip().split()
                mapping[normalize_word(what)] = normalize_word(to)
        return mapping

class EvaluationDataset(object):
    def __init__(self, name, path, word_mapping):
        self.name = name
        self._examples = self._read_examples(path)
        self._word_mapping = word_mapping

    def __iter__(self):
        return iter(self._examples)

    def get_vocabulary(self):
        words = []
        for example in self._examples:
            words.extend(example[:2])
        return set(words)

    def check_vocabulary(self, known_words, verbose=False):
        logger = logging.getLogger(__name__)

        logger.info('Checking vocabulary of {}'.format(self.name))

        if verbose:
            logger.info('Word mapping has {} words.'.format(len(self._word_mapping)))
            for w1, w2 in self._word_mapping.iteritems():
                if w2 not in known_words:
                    logger.info('Warning: Word {} used in the mapping is not known.'.format(w2))

        matched_words = 0
        mapped_words = 0
        missing_words = 0
        matched_examples = 0
        skipped_examples = 0

        for word in self.get_vocabulary():
            maybe_mapped = self._maybe_map(word)

            if maybe_mapped in known_words:
                matched_words += 1
                if self._is_mapped(word):
                    mapped_words += 1
            else:
                if verbose:
                    logger.info('Missing: {}'.format(word))
                missing_words += 1

        for (w1, w2, _) in self._examples:
            if self._maybe_map(w1) in known_words and self._maybe_map(w2) in known_words:
                matched_examples += 1
            else:
                skipped_examples += 1

        logger.info('Words: {} matched (of which {} mapped), {} missing.'.format(matched_words, mapped_words, missing_words))
        logger.info('Examples: {} matched, {} skipped.'.format(matched_examples, skipped_examples))

    def evaluate(self, word2embedding):
        logger = logging.getLogger(__name__)

        test_scores = []
        my_scores = []

        matched_examples = 0
        skipped_examples = 0
        for (w1, w2, score) in self._examples:
            w1 = self._maybe_map(w1)
            w2 = self._maybe_map(w2)
            if w1 in word2embedding and w2 in word2embedding:
                matched_examples += 1
                my_scores.append(self._score(word2embedding[w1], word2embedding[w2]))
                test_scores.append(score)
            else:
                skipped_examples += 1

        spearman = stats.stats.spearmanr(my_scores, test_scores)[0]

        logger.info("{}: Spearman: {:.4}, matched {}, skipped {}.".format(self.name, spearman, matched_examples, skipped_examples))

        return spearman, matched_examples, skipped_examples

    def _maybe_map(self, word):
        if word in self._word_mapping:
            return self._word_mapping[word]
        else:
            return word

    def _is_mapped(self, word):
        return word in self._word_mapping

    @staticmethod
    def _read_examples(path):
        with open(path, 'r') as dataset:
            examples = []
            for line in dataset:
                words = line.rstrip().split()
                examples.append((normalize_word(words[0]), normalize_word(words[1]), float(words[2])))
            return examples

    @staticmethod
    def _score(vec1, vec2):
        return dot(vec1, vec2) / (linalg.norm(vec1) * linalg.norm(vec2))

class EvaluationReport(object):
    def __init__(self, path):
        self._path = path

    def create(self, records):
        with open(self._path, "wb") as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'score', 'matched', 'skipped'])
            writer.writerows(records)
