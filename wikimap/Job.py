import time
import os
import Paths
import logging

class CompletionGuard(object):
    def __init__(self, files):
        self._files = files

    def __enter__(self):
        self._completed = False
        return self

    def __exit__(self, type, value, traceback):
        if not self._completed:
            for f in self._files:
                if os.path.isfile(f):
                    os.remove(f)

    def complete(self):
        self._completed = True

class DependencyChecker(object):
    def __init__(self, job_name, dependencies):
        self._job_name = job_name
        self._dependencies = dependencies

    def __enter__(self):
        Paths.expected_paths.set(self._dependencies)
        return self

    def __exit__(self, type, value, traceback):
        Paths.expected_paths.clear()

    def check(self):
        logger = logging.getLogger(__name__)
        unexpected, missing = Paths.expected_paths.report()
        for path in unexpected:
            logger.warning("Unspecified dependency of '{}': on {}".format(self._job_name, path))
        for path in missing:
            logger.warning("Unnecessary dependency of '{}': on {}".format(self._job_name, path))
        return len(missing) == 0 and len(unexpected) == 0

class Job(object):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'
    ABORTED = 'ABORTED'
    WARNING = 'WARNING'

    def __init__(self, name, task, inputs=None, outputs=None, tag="", noskip=False, **kwargs):
        self._task = task

        self.name = name
        self._inputs = inputs or []
        self._outputs = outputs or []

        self.tag = tag
        self.noskip = noskip
        self.config = kwargs

        self.duration = 0
        self.outcome = 'NONE'

    def run(self):
        t0 = time.time()
        try:
            with DependencyChecker(self.name, self.inputs() + self.outputs()) as dependencies:
                with CompletionGuard(self.outputs()) as guard:
                    self._task(**self.config)
                    self.outcome = Job.SUCCESS
                    guard.complete()
                deps_ok = dependencies.check()
                if not deps_ok:
                    self.outcome = Job.WARNING
        except KeyboardInterrupt:
            self.outcome = Job.ABORTED
            raise
        except:
            self.outcome = Job.FAILURE
            raise
        finally:
            self.duration = time.time() - t0

    def inputs(self, base=None):
        return Paths.resolve(self._inputs, base=base)

    def outputs(self, base=None):
        return Paths.resolve(self._outputs, base=base)

    def skip(self):
        self.outcome = Job.SKIPPED
