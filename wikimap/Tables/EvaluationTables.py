from ..DataHelpers import normalize_word
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

class SimilarityDataset(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.type = 'similarity'

    def __iter__(self):
        with open(self.path, 'r') as dataset:
            for line in dataset:
                words = line.rstrip().split()
                yield ((normalize_word(words[0]), normalize_word(words[1])), float(words[2]))

class BlessRelationDataset(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.type = 'relation'

    def __iter__(self):
        with open(self.path, 'r') as dataset:
            for line in dataset:
                words = line.rstrip().split()
                yield map(normalize_word, words)

class EvaluationReport(object):
    def __init__(self, path):
        self._path = path

    def create(self, records):
        with open(self._path, "wb") as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'type', 'method', 'score', 'matched_examples', 'skipped_examples'])
            writer.writeheader()
            writer.writerows(records)
