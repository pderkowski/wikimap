from ..Utils import Colors
from .. import Utils
from Job import Job

class Build(object):
    def __init__(self, jobs):
        self._jobs = jobs
        for i, job in enumerate(self._jobs):
            job.number = i

    def __iter__(self):
        return iter(self._jobs)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._get_job_by_number(key)
        else:
            try:
                return self._get_job_by_name(key)
            except KeyError:
                return self._get_job_by_alias(key)

    def __len__(self):
        return len(self._jobs)

    def _get_job_by_name(self, key):
        for job in self._jobs:
            if job.name == key:
                return job
        raise KeyError('No job found with a given name.')

    def _get_job_by_alias(self, key):
        for job in self._jobs:
            if job.alias == key:
                return job
        raise KeyError('No job found with a given alias.')

    def _get_job_by_number(self, key):
        for job in self._jobs:
            if job.number == key:
                return job
        raise KeyError('No job found with a given number.')

    def get_summary_str(self):
        outcome_2_color = {
            Job.SUCCESS: Colors.GREEN,
            Job.FAILURE: Colors.RED,
            Job.SKIPPED: Colors.BLUE,
            Job.ABORTED: Colors.YELLOW,
            Job.WARNING: Colors.YELLOW,
            Job.NOT_RUN: Colors.RED
        }

        def make_summary_row(job):
            return (str(job.number),
                job.name,
                Utils.color_text('[{}]'.format(job.outcome), outcome_2_color[job.outcome]),
                Utils.format_duration(job.duration))

        rows = [make_summary_row(job) for job in self]
        return Utils.make_table(('#', 'JOB NAME', 'OUTCOME', 'DURATION'), rows, ('r', 'l', 'c', 'c'))

    def get_job_list_str(self):
        return Utils.make_table(['#', 'ALIAS', 'JOB NAME'], [[str(job.number), job.alias, job.name] for job in self], ['r', 'l', 'l'])

    def save_summary(self, path):
        with open(path, 'w') as output:
            output.write(self.get_summary_str()+'\n')
