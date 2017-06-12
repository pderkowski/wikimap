from ..DataHelpers import pipe, NotBlankIt, NotCommentIt
from ..Utils import make_table
import csv
import logging


class SimilarityDataset(object):
    def __init__(self, name, path, word_mapper=int,
                 word1_col=0, word2_col=1, score_col=2):
        self.name = name
        self.path = path
        self.type = 'similarity'
        self._word_mapper = word_mapper
        self._word1_col = word1_col
        self._word2_col = word2_col
        self._score_col = score_col

    def __iter__(self):
        with open(self.path, 'r') as dataset:
            for line in pipe(dataset, NotBlankIt, NotCommentIt):
                words = line.rstrip().split()
                yield (
                    self._map(words[self._word1_col]),
                    self._map(words[self._word2_col]),
                    float(words[self._score_col])
                )

    def _map(self, word):
        try:
            return self._word_mapper(word)
        except KeyError:
            return None


class TripletDataset(object):
    def __init__(self, name, path, word_mapper=int):
        self.name = name
        self.path = path
        self.type = 'triplet'
        self._word_mapper = word_mapper

    def __iter__(self):
        with open(self.path, 'r') as dataset:
            for line in pipe(dataset, NotBlankIt, NotCommentIt):
                try:
                    words = line.rstrip().split()
                    yield map(self._map, words)
                except KeyError:
                    pass

    def _map(self, word):
        try:
            return self._word_mapper(word)
        except KeyError:
            return None


class InvalidRecord(Exception):
    def __init__(self, message):
        super(InvalidRecord, self).__init__(message)


class EvaluationReport(object):
    field_names = ['name', 'type', 'method', 'score', 'matched_examples', 'skipped_examples']
    short_field_names = ['name', 'type', 'method', 'score', 'matched', 'skipped']
    field_types = {'name': str, 'type': str, 'method': str, 'score': float, 'matched_examples': int, 'skipped_examples': int}

    def __init__(self, path):
        self._path = path
        self._logger = logging.getLogger(__name__)

    def create(self, records):
        with open(self._path, "wb") as f:
            records = list(records)
            try:
                self._validate(records)
                writer = csv.DictWriter(f, fieldnames=EvaluationReport.field_names)
                writer.writeheader()
                writer.writerows(records)
            except InvalidRecord, r:
                self._logger.error('Invalid record {}'.format(r))

    def __iter__(self):
        with open(self._path, "rb") as f:
            reader = csv.DictReader(f)
            rows = list(self._map_types(reader))
            self._validate(rows)
            return iter(rows)

    def get_pretty_table(self):
        rows = [[row[f] for f in EvaluationReport.field_names] for row in self]
        return make_table(EvaluationReport.short_field_names, rows, ['l', 'l', 'l', 'r', 'r', 'r'], float_format='.3')

    def get_scores(self):
        return [(row['name'], row['score']) for row in self]

    def get_test_names(self):
        return [row['name'] for row in self]

    def _map_types(self, rows):
        for row in rows:
            for field, value in row.iteritems():
                row[field] = EvaluationReport.field_types[field](value)
            yield row

    def _validate(self, records):
        for r in records:
            expected = set(EvaluationReport.field_names)
            actual = set(r.keys())
            if expected != actual:
                raise InvalidRecord(str(r)+'\n\
                    Expected fields  {}\n\
                    Actual fields: {}'.format(str(expected), str(actual)))
            for field, type_ in EvaluationReport.field_types.iteritems():
                if not isinstance(r[field], type_):
                    raise InvalidRecord(str(r)+'\n\
                        Field {}:\n\
                        Expected type: {}\n\
                        Actual type: {}'.format(field, str(type_), str(type(field))))
