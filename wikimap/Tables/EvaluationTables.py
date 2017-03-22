from ..DataHelpers import normalize_word
from ..Utils import make_table
import csv
import logging

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
