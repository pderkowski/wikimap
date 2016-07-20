import logging
import time
import Utils
import sys

class Job(object):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'
    INTERRUPT = 'INTERRUPT'

    def __init__(self, title, invoke, skipCondition=None):
        self.title = title
        self.invoke = invoke
        self.skipCondition = skipCondition

        self.duration = 0
        self.outcome = 'NONE'

    def run(self):
        t0 = time.time()
        try:
            if self.skipCondition and self.skipCondition():
                self.outcome = Job.SKIPPED
            else:
                self.invoke()
                self.outcome = Job.SUCCESS
        except KeyboardInterrupt:
            self.outcome = Job.INTERRUPT
            raise
        except:
            self.outcome = Job.FAILURE
            raise
        finally:
            self.duration = time.time() - t0

class Jobs(object):
    def __init__(self):
        self.jobs = []

    def add(self, job):
        self.jobs.append(job)

    def run(self):
        logger = logging.getLogger(__name__)

        summary = []
        for job in self.jobs:
            logger.info('STARTING JOB: {}'.format(job.title))

            try:
                job.run()
                summary.append((job.outcome, job.title, job.duration))
            except KeyboardInterrupt:
                summary.append((job.outcome, job.title, job.duration))
                self._printSummary(summary)
                sys.exit(1)
            except Exception, e:
                logger.exception(str(e))
                summary.append((job.outcome, job.title, job.duration))
                self._printSummary(summary)
                sys.exit(1)

        self._printSummary(summary)

    def _printSummary(self, summary):
        print '-'*80
        print '{:30} |  OUTCOME  |  DURATION   |'.format('JOB SUMMARY')
        print '-'*80

        OKGREEN = '\033[92m'
        OKBLUE = '\033[94m'
        FAILRED = '\033[91m'
        ENDCOLOR = '\033[0m'
        WARNING = '\033[93m'

        for outcome, title, duration in summary:
            if outcome == 'SUCCESS':
                COLOR = OKGREEN
            elif outcome == 'FAILURE':
                COLOR = FAILRED
            elif outcome == 'SKIPPED':
                COLOR = OKBLUE
            else:
                COLOR = WARNING

            print '{:30} | {}[{}]{} | {} |'.format(title, COLOR, outcome, ENDCOLOR, Utils.formatDuration(duration))

        print '-'*80