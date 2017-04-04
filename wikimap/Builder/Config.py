import ast
from pprint import pprint, pformat

class BuildConfig(object):
    def __init__(self, config):
        self._config = config

    @staticmethod
    def from_string(config_string):
        return BuildConfig(ast.literal_eval(config_string))

    @staticmethod
    def from_build(build):
        config = {}
        for job in build:
            for arg, value in job.config.iteritems():
                config_key = '{}.{}'.format(job.alias, arg)
                config[config_key] = value
        return BuildConfig(config)

    @staticmethod
    def from_path(config_path):
        with open(config_path, 'r') as config_file:
            return BuildConfig.from_string(config_file.read())

    def get_job_config(self, job_alias):
        job_config = {}
        for config_key, value in self._config.iteritems():
            alias, arg_name = config_key.split('.')
            if alias == job_alias:
                job_config[arg_name] = value
        return job_config

    def save(self, path):
        with open(path, 'w') as output:
            pprint(self._config, output)

    def __str__(self):
        return pformat(self._config)

    def __getitem__(self, key):
        return self._config[key]
