# -*- coding: utf-8 -*-

import os
import ast
from Explorer import BuildExplorer
import plotly
from plotly.graph_objs import Scatter, Layout, Figure
from .. import Utils

class InvalidConfigException(Exception):
    pass

class ReportConfig(object):
    @staticmethod
    def from_string(string):
        return ReportConfig(ast.literal_eval(string))

    def __init__(self, config):
        if not isinstance(config, dict):
            raise InvalidConfigException('Expected a dict.')

        self._config = dict(config)

        required_args = [
            ('filename', str, None),
            ('dest_dir', str, None),
            ('indices', str, None),
            ('builds_dir', str, None),
            ('build_prefix', str, None)
        ]
        optional_args = [
            ('included_tests', (list, str), 'all'),
            ('title', str, 'No title')
        ]

        self._check_if_present(required_args)
        self._set_defaults_if_missing(optional_args)
        self._check_if_types_match(required_args+optional_args)

        self._config['dest_dir'] = os.path.realpath(self._config['dest_dir'])
        self._config['dest_path'] = os.path.join(self._config['dest_dir'], self._config['filename'])
        self._config['indices'] = Utils.parse_int_range(self._config['indices'])

        if self._config['included_tests'] == 'all':
            self._config['included_tests'] = self._get_all_test_names()


    def _check_if_present(self, args):
        for (arg_name, _1, _2) in args:
            if arg_name not in self._config:
                raise InvalidConfigException("Missing parameter '{}'.".format(arg_name))

    def _set_defaults_if_missing(self, args):
        for (arg_name, _, arg_default) in args:
            if arg_name not in self._config:
                self._config[arg_name] = arg_default

    def _check_if_types_match(self, args):
        for (arg_name, arg_type, _) in args:
            if not isinstance(self._config[arg_name], arg_type):
                raise InvalidConfigException("Wrong type of parameter '{}'. Expected {}, got {}.".format(
                    arg_name, str(arg_type), str(type(self._config[arg_name]))))

    def _get_all_test_names(self):
        build_explorer = BuildExplorer(self._config['builds_dir'], self._config['build_prefix'])
        test_names = set([])
        for i in self._config['indices']:
            names = build_explorer.get_data(i).get_evaluation_test_names()
            test_names.update(names)
        return sorted(list(test_names))

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def get(self):
        return self._config


class Report(object):
    def __init__(self, config):
        self._config = config
        self._build_explorer = BuildExplorer(self._config['builds_dir'], self._config['build_prefix'])

    def create(self):
        logger = Utils.get_logger(__name__)
        logger.info(Utils.thick_line_separator)
        logger.info('Generating report: {}'.format(self._config['title']))
        logger.info(Utils.thick_line_separator)

        data = self._select_data()
        self._plot(data)

    def _select_data(self):
        def filter_tests(series):
            series['test_scores'] = [(name, score) for name, score in series['test_scores'] if name in self._config['included_tests']]
            return series

        data_series = self._get_data_series()
        return [filter_tests(s) for s in data_series]

    def _get_data_series(self):
        build_explorer = BuildExplorer(self._config['builds_dir'], self._config['build_prefix'])
        series = []
        for index in self._config['indices']:
            series.append({
                'name': build_explorer.get_build_name(index),
                'test_scores': sorted(build_explorer.get_data(index).get_evaluation_scores(), key=lambda x: x[0])
            })
        return series

    def _plot(self, data):
        logger = Utils.get_logger(__name__)

        traces = [
            Scatter(
                name=series['name'],
                x=[s[0] for s in series['test_scores']],
                y=[s[1] for s in series['test_scores']]
            ) for series in data
        ]

        layout = Layout(
            title=self._config['title']
        )

        figure = Figure(data=traces, layout=layout)

        Utils.make_dir_if_not_exists(os.path.dirname(self._config['dest_path']))
        plotly.offline.plot(figure, filename=self._config['dest_path'])
        logger.info('Saving report to {}'.format(self._config['dest_path']))
