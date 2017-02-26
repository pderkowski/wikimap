from ..DataHelpers import normalize_word
from scipy import stats, linalg
from numpy import dot
import logging

class EvaluationDataset(object):
    def __init__(self, path):
        self._examples = self._read_examples(path)

    def __iter__(self):
        return iter(self._examples)

    def get_vocabulary(self):
        words = []
        for example in self._examples:
            words.extend(example[:2])
        return set(words)

    def _read_examples(self, path):
        with open(path, 'r') as dataset:
            examples = []
            for line in dataset:
                words = line.rstrip().split()
                examples.append((normalize_word(words[0]), normalize_word(words[1]), float(words[2])))
            return examples

    def check_vocabulary(self, known_words):
        logger = logging.getLogger(__name__)

        matched_words = 0
        missing_words = 0
        matched_pairs = 0
        skipped_pairs = 0

        for word in self.get_vocabulary():
            if word in known_words:
                matched_words += 1
            else:
                missing_words += 1

        for (w1, w2, _) in self._examples:
            if w1 in known_words and w2 in known_words:
                matched_pairs += 1
            else:
                skipped_pairs += 1

        logger.info('Words: {} matched, {} missing.'.format(matched_words, missing_words))
        logger.info('Pairs: {} matched, {} skipped.'.format(matched_pairs, skipped_pairs))

    def evaluate(self, word2embedding):
        test_scores = []
        my_scores = []

        matched_pairs = 0

        for (w1, w2, score) in self._examples:
            if w1 in word2embedding and w2 in word2embedding:
                matched_pairs += 1
                my_scores.append(self._score(word2embedding[w1], word2embedding[w2]))
                test_scores.append(score)

        return stats.stats.spearmanr(my_scores, test_scores)[0], matched_pairs

    @staticmethod
    def _score(vec1, vec2):
        return dot(vec1, vec2) / (linalg.norm(vec1) * linalg.norm(vec2))

# def get_vocabulary_stats():
#     vocabulary = Tables.EvaluationDataset(Paths.wordsim353_all()).get_vocabulary()
#     disamb_title2id = Tables.TitleIndex(Paths.title_index())
#     id2real_title = dict(Tables.PageTable(Paths.pages()).select_id_title_of_articles())
#     embedding_ids = set(Tables.EmbeddingsTable(Paths.embeddings()).keys())
#     return Helpers.get_existing_remapped_missing_words(vocabulary, disamb_title2id, id2real_title, embedding_ids)


# def get_existing_remapped_missing_words(vocabulary, disamb_title2id, id2real_title, embedding_ids):
#     existing, remapped, missing = [], [], []
#     for word in vocabulary:
#         word = normalize_word(word)
#         if word not in disamb_title2id: # there is no such title
#             missing.append(word)
#         elif disamb_title2id[word] not in embedding_ids: # title exists, but does not point to an embedding
#             missing.append(word)
#         else:
#             mapped_word = normalize_word(id2real_title[disamb_title2id[word]])
#             if word == mapped_word: # the mapped word is the same as the sane as the original
#                 existing.append(word)
#             else: # it's not the same, for example redirection or disambiguation
#                 remapped.append((word, mapped_word))
#     return existing, remapped, missing


# import os

# import sys
# import logging
# import argparse
# import numpy
# from collections import defaultdict
# from scipy import linalg, mat, dot, stats
# DATA_ROOT = os.path.dirname( os.path.abspath( __file__ ) ) + "/data/"

# class Wordsim:
#     def __init__(self,lang):
#         logging.info("collecting datasets ..")
#         self.files = [ file_name.replace(".txt","") for file_name in os.listdir(DATA_ROOT+lang) if ".txt" in file_name ]
#         self.dataset=defaultdict(list)
#         for file_name in self.files:
#             for line in open(DATA_ROOT + lang + "/" + file_name + ".txt"):
#                 self.dataset[file_name].append([ float(w) if i == 2 else w for i, w in enumerate(line.strip().split())])

#     @staticmethod
#     def cos(vec1,vec2):
#         return vec1.dot(vec2)/(linalg.norm(vec1)*linalg.norm(vec2))

#     @staticmethod
#     def rho(vec1,vec2):
#         return stats.stats.spearmanr(vec1, vec2)[0]

#     @staticmethod
#     def load_vector(path):
#         try:
#             logging.info("loading vector ..")
#             if path[-3:] == ".gz":
#                 import gzip
#                 f = gzip.open(path, "rb")
#             else:
#                 f = open(path, "rb")
#         except ValueError:
#             print "Oops!  No such file.  Try again .."
#         word2vec = {}
#         for wn, line in enumerate(f):
#             line = line.lower().strip()
#             word = line.split()[0]
#             word2vec[word] = numpy.array(map(float,line.split()[1:]))
#         logging.info("loaded vector {0} words found ..".format(len(word2vec.keys())))
#         return word2vec

#     @staticmethod
#     def pprint(result):
#         from prettytable import PrettyTable
#         x = PrettyTable(["Dataset", "Found", "Not Found", "Score (rho)"])
#         x.align["Dataset"] = "l"
#         for k, v in result.items():
#             x.add_row([k,v[0],v[1],v[2]])
#         print x

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--lang', '-l', default="en")
#     parser.add_argument('--vector', '-v', default="")
#     args = parser.parse_args()
#     wordsim = Wordsim(args.lang)
#     word2vec = wordsim.load_vector(args.vector)
#     result = wordsim.evaluate(word2vec)
#     wordsim.pprint(result)
