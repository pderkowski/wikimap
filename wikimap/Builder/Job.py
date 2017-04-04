import os
from .. import Utils
from ..Data import Data
from ..Paths import CheckedPaths, AbstractPathGroup
from abc import ABCMeta, abstractmethod

class InvalidConfig(Exception):
    pass

class Properties(object):
    Forced = 1

class CompletionGuard(object):
    def __init__(self, files):
        self._files = files
        self._completed = False

    def __enter__(self):
        self._completed = False
        return self

    def __exit__(self, _1, _2, _3):
        if not self._completed:
            for f in self._files:
                if os.path.isfile(f):
                    os.remove(f)

    def complete(self):
        self._completed = True

class Job(object):
    __metaclass__ = ABCMeta

    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'
    ABORTED = 'ABORTED'
    WARNING = 'WARNING'
    NOT_RUN = 'NOT RUN'

    def __init__(self, name, alias="", inputs=None, outputs=None, **kwargs):
        self.name = name
        self.number = -1
        self.inputs = AbstractPathGroup(inputs or [])
        self.outputs = AbstractPathGroup(outputs or [])

        self.alias = alias
        self.config = kwargs
        self.duration = 0
        self.outcome = Job.NOT_RUN
        self.properties = []
        self.logs = []

        self.data = None

        self._logger = Utils.get_logger(__name__)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    def run(self, base):
        timer = Utils.SimpleTimer()
        try:
            paths = CheckedPaths(base, (self.inputs + self.outputs)(base))
            self.data = Data(paths)
            with CompletionGuard(self.outputs(base)) as guard:
                self(**self.config)
                self.outcome = Job.SUCCESS
                guard.complete()
                if paths.has_invalid_dependencies():
                    self.outcome = Job.WARNING
                    unexpected, missing = paths.get_invalid_dependencies()
                    for path in unexpected:
                        message = 'Unexpected dependency of {} on {}'.format(self.name, path)
                        self.logs.append(message)
                        self._logger.info(message)
                    for path in missing:
                        message = 'Missing dependency of {} on {}'.format(self.name, path)
                        self.logs.append(message)
                        self._logger.info(message)

        except KeyboardInterrupt:
            self.outcome = Job.ABORTED
            raise
        except:
            self.outcome = Job.FAILURE
            raise
        finally:
            self.duration = timer()

    def skip(self):
        self.outcome = Job.SKIPPED

    def configure(self, config):
        for arg_name, arg_value in config.iteritems():
            try:
                self.config[arg_name] = arg_value
            except KeyError:
                raise InvalidConfig('Unexpected argument: {} to job: {}.'.format(arg_name, self.name))

    def is_forced(self):
        return Properties.Forced in self.properties
