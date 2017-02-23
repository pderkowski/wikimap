import time
import os
import Paths

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

class Job(object):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'
    INTERRUPT = 'INTERRUPT'

    def __init__(self, name, task, inputs=[], outputs=[], artifacts=[], noskip=False, **kwargs):
        self._task = task

        self.name = name
        self._inputs = inputs
        self._outputs = outputs
        self._artifacts = artifacts

        self.noskip = noskip
        self.config = kwargs

        self.duration = 0
        self.outcome = 'NONE'

    def run(self):
        t0 = time.time()
        try:
            outputPaths = self.outputs()
            guardedPaths = self.outputs() + self.artifacts()
            with CompletionGuard(guardedPaths) as guard:
                inputPaths = self.inputs()
                args = inputPaths + outputPaths
                self._task(*args, **self.config)
                self.outcome = Job.SUCCESS
                guard.complete()
        except KeyboardInterrupt:
            self.outcome = Job.INTERRUPT
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

    def artifacts(self, base=None):
        return Paths.resolve(self._artifacts, base=base)

    def skip(self):
        self.outcome = Job.SKIPPED
