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
        self.inputs = inputs
        self.outputs = outputs
        self.artifacts = artifacts

        self.noskip = noskip
        self.config = kwargs

        self.duration = 0
        self.outcome = 'NONE'

    def run(self):
        t0 = time.time()
        try:
            outputPaths = Paths.resolve(self.outputs)
            guardedPaths = Paths.resolve(self.outputs + self.artifacts)
            with CompletionGuard(guardedPaths) as guard:
                inputPaths = Paths.resolve(self.inputs)
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

    def skip(self):
        self.outcome = Job.SKIPPED


