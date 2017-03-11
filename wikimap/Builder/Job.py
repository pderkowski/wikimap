from PathUtils import DependencyChecker, CompletionGuard, resolve
from Utils import SimpleTimer

class Job(object):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'
    ABORTED = 'ABORTED'
    WARNING = 'WARNING'

    def __init__(self, name, task, number, inputs=None, outputs=None, tag="", **kwargs):
        self.task = task
        self.name = name
        self.number = number
        self._inputs = inputs or []
        self._outputs = outputs or []

        self.tag = tag
        self.config = kwargs
        self.duration = 0
        self.outcome = 'NONE'

    def run(self):
        timer = SimpleTimer()
        try:
            with DependencyChecker(self.name, self.inputs() + self.outputs()), CompletionGuard(self.outputs()) as guard:
                self.task(**self.config)
                self.outcome = Job.SUCCESS
                guard.complete()
                if not DependencyChecker.is_ok():
                    self.outcome = Job.WARNING
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
