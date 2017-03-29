# -*- coding: utf-8 -*-

from Explorer import BuildExplorer
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
import os

class DataTableException(Exception):
    pass

class DataTable(object):
    def __init__(self):
        self._columns = []
        self._row_map = {}

    def add_column(self, column_name, column):
        if not self._columns:
            self._add_first_column(column_name, column)
        else:
            self._add_normal_column(column_name, column)

    def get_data_as_rows(self):
        if not self._columns:
            return [[]]
        else:
            rows = []
            rows_count = len(self._columns[0])
            for i in range(rows_count):
                row = [column[i] for column in self._columns]
                rows.append(row)
            return rows

    def _add_first_column(self, column_name, column):
        if not isinstance(column, list):
            raise DataTableException('First column must be a list.')

        self._columns = [[column_name]+column]
        for i, item in enumerate(column):
            if item in self._row_map:
                raise DataTableException('First column must contain unique values.')
            self._row_map[item] = i

    def _add_normal_column(self, column_name, column):
        if isinstance(column, list):
            if len(column) + 1 != len(self._columns[0]): # +1 because we add column_name to column
                raise DataTableException('Adding a column that is not the same size as the others.')
            self._columns.append([column_name]+column)
        elif isinstance(column, dict):
            placeholders = [None for _ in self._columns[0][1:]]
            for row_name, item in column.iteritems():
                if row_name not in self._row_map:
                    print self._row_map.items()
                    raise DataTableException('Unrecognized row name: {}.'.format(row_name))
                placeholders[self._row_map[row_name]] = item
            self._columns.append([column_name]+placeholders)
        else:
            raise DataTableException('Column must be either a list or a dict.')

class ReportCreator(object):
    def __init__(self, buildpath, build_prefix):
        self._build_explorer = BuildExplorer(buildpath, build_prefix)

    def make_plot(self, build_indices, path):
        table = DataTable()
        table.add_column('Test name', sorted(self._get_test_names(build_indices)))
        for index in build_indices:
            build_name = self._build_explorer.get_build_name(index)
            scores = self._get_scores(index) # dict {test_name -> score}
            try:
                table.add_column(build_name, scores)
            except DataTableException, e:
                print build_name
                print scores
                raise e
        self._render_plot(table.get_data_as_rows(), path)

    def _get_scores(self, index):
        return dict(self._build_explorer.get_data(index).get_evaluation_scores())

    def _get_test_names(self, build_indices):
        test_names = set([])
        for index in build_indices:
            test_names.update(self._build_explorer.get_data(index).get_evaluation_test_names())
        return list(test_names)

    def _render_plot(self, table, output_path):
        templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        env = Environment(
            loader=FileSystemLoader(templates_path),
            autoescape=select_autoescape(['html', 'xml'])
        )

        template = env.get_template('report.html')
        with open(output_path, 'w') as output:
            template.stream(headers=json.dumps(table[0]), rows=json.dumps(table[1:])).dump(output)
