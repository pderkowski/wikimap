# -*- coding: utf-8 -*-

import os
import ast
from Extractor import DataExtractor
from .. import Utils
import plotly
from plotly.graph_objs import Scatter, Layout, Figure
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json

class InvalidConfigException(Exception):
    pass

class ReportConfig(object):
    @staticmethod
    def from_string(string):
        return ReportConfig(ast.literal_eval(string))

    def __init__(self, config):
        if not isinstance(config, dict):
            raise InvalidConfigException('Expected a dict.')

        self._logger = Utils.get_logger(__name__)
        self._config = dict(config)


        required_args = [
            ('filename', str, None),
            ('dest_dir', str, None),
            ('indices', str, None),
            ('builds_dir', str, None),
            ('build_prefix', str, None)
        ]
        optional_args = [
            ('tests', (list, str), 'all'),
            ('title', str, 'No title'),
            ('best_builds_per_test', int, 10),
            ('tooltip', list, [])
        ]

        self._check_if_present(required_args)
        self._set_defaults_if_missing(optional_args)
        self._check_if_types_match(required_args+optional_args)

        self._config['dest_dir'] = os.path.realpath(self._config['dest_dir'])
        self._config['dest_path'] = os.path.join(self._config['dest_dir'], self._config['filename'])
        self._config['indices'] = Utils.parse_int_range(self._config['indices'])

        if self._config['tests'] == 'all':
            self._config['tests'] = DataExtractor(self._config['builds_dir'], self._config['build_prefix']).get_test_names(self._config['indices'])

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

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def get(self):
        return self._config

class Selection(object):
    def __init__(self, config):
        self._config = config

    def apply_to(self, data):
        data = self._select_n_best_per_test(data)
        return data

    def _select_n_best_per_test(self, data):
        n = self._config['best_builds_per_test']
        selected = set()
        for col in data.columns:
            best = data.nlargest(n, col).index.tolist()
            selected.update(best)
        selected = sorted(list(selected))
        return data.filter(items=selected, axis='index')

class Report(object):
    def __init__(self, config):
        self._logger = Utils.get_logger(__name__)
        self._config = config
        self._extractor = DataExtractor(self._config['builds_dir'], self._config['build_prefix'])

    def create(self):
        self._logger.info(Utils.thick_line_separator)
        self._logger.info('Generating report: {}'.format(self._config['title']))
        self._logger.info(Utils.thin_line_separator)

        self._logger.info('Config:')
        for arg, val in sorted(self._config.get().iteritems()):
            self._logger.info(' {}: {}'.format(arg, repr(val)))
        self._logger.info(Utils.thin_line_separator)

        data = self._extractor.get_test_scores(self._config['indices'], self._config['tests'])
        selected_data = Selection(self._config).apply_to(data)

        self._logger.info('Data:')
        self._logger.info(selected_data)
        self._logger.info(Utils.thin_line_separator)

        plot_html = self._make_plot(selected_data)
        table_html = self._make_table(selected_data)
        self._render_report(plot_html, table_html)

        self._logger.info(Utils.thick_line_separator)

    def _make_plot(self, data):
        traces = [
            Scatter(
                name=name,
                x=data.columns,
                y=scores,
                text=self._make_tooltip(name)
            ) for name, scores in data.iterrows()
        ]

        layout = Layout(
            title=self._config['title'],
            hovermode='closest'
        )

        figure = Figure(data=traces, layout=layout)

        return plotly.offline.plot(figure, output_type='div')

    def _make_tooltip(self, build_name):
        build_config = [(config_arg, self._extractor.get_config_value(build_name, config_arg)) for config_arg in self._config['tooltip']]
        build_config_strings = ['{}: {}'.format(a, v) for a, v in build_config]
        return '\n'.join(build_config_strings)

    def _make_table(self, data):
        return data.to_html(classes='table table-bordered', float_format="{:.3f}".format)

    def _render_report(self, plot_html, table_html):
        resources_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report_rsc')
        env = Environment(
            loader=FileSystemLoader(resources_path),
            autoescape=select_autoescape(['html', 'xml'])
        )

        template = env.get_template('report.html')
        with open(self._config['dest_path'], 'w') as output:
            Utils.make_dir_if_not_exists(os.path.dirname(self._config['dest_path']))
            self._logger.info('Saving report to {}'.format(self._config['dest_path']))
            template.stream(plot=plot_html, table=table_html).dump(output)
