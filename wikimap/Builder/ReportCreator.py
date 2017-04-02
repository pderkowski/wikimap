# -*- coding: utf-8 -*-

import os
from Explorer import BuildExplorer
import plotly
from plotly.graph_objs import Scatter
from .. import Utils

class ReportCreator(object):
    def __init__(self, builds_dir, build_prefix):
        self._build_explorer = BuildExplorer(builds_dir, build_prefix)

    def create(self, build_indices, output_path, included_tests=None):
        included_tests = included_tests or self._get_test_names(build_indices)
        data = self._select_data(build_indices, included_tests=included_tests)
        self._plot(data, output_path)

    def _select_data(self, build_indices, included_tests):
        def filter_tests(series):
            series['test_scores'] = [(name, score) for name, score in series['test_scores'] if name in included_tests]
            return series

        results = self._get_data_series(build_indices)
        return [filter_tests(r) for r in results]

    def _get_data_series(self, build_indices):
        series = []
        for index in build_indices:
            series.append({
                'name': self._build_explorer.get_build_name(index),
                'test_scores': sorted(self._build_explorer.get_data(index).get_evaluation_scores(), key=lambda x: x[0])
            })
        return series

    def _get_test_names(self, build_indices):
        test_names = set([])
        for i in build_indices:
            names = self._build_explorer.get_data(i).get_evaluation_test_names()
            test_names.update(names)
        return sorted(list(test_names))

    def _plot(self, data, output_path):
        traces = [
            Scatter(
                name=series['name'],
                x=[s[0] for s in series['test_scores']],
                y=[s[1] for s in series['test_scores']]
            ) for series in data
        ]

        Utils.make_dir_if_not_exists(os.path.dirname(output_path))
        plotly.offline.plot(traces, filename=output_path)
