from PathUtils import DependencyChecker, CompletionGuard, resolve
from Utils import SimpleTimer
from abc import ABCMeta, abstractmethod

class Properties(object):
    Forced = 1

class Job(object):
    __metaclass__ = ABCMeta

    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'
    ABORTED = 'ABORTED'
    WARNING = 'WARNING'
    NOT_RUN = 'NOT RUN'

    def __init__(self, name, tag="", inputs=None, outputs=None, **kwargs):
        self.name = name
        self.number = -1
        self._inputs = inputs or []
        self._outputs = outputs or []

        self.tag = tag
        self.config = kwargs
        self.duration = 0
        self.outcome = Job.NOT_RUN
        self.properties = []
        self.logs = []
        self.warnings = []

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    def run(self):
        timer = SimpleTimer()
        try:
            with DependencyChecker(self.name, self.inputs() + self.outputs()), CompletionGuard(self.outputs()) as guard:
                self(**self.config)
                self.outcome = Job.SUCCESS
                guard.complete()
                if not DependencyChecker.is_ok():
                    self.outcome = Job.WARNING
                    self.warnings.extend(DependencyChecker.get_warnings())

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

    def inputs(self, base=None):
        return resolve(self._inputs, base=base)

    def outputs(self, base=None):
        return resolve(self._outputs, base=base)
