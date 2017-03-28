from ..Utils import Colors
from .. import Utils
from Job import Job

class Build(object):
    def __init__(self, jobs):
        self._logger = Utils.get_logger(__name__)
        self._jobs = jobs
        for i, job in enumerate(self._jobs):
            job.number = i
        self._custom_config = {}

    def __iter__(self):
        return iter(self._jobs)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._get_job_by_number(key)
        else:
            try:
                return self._get_job_by_name(key)
            except KeyError:
                return self._get_job_by_tag(key)

    def __len__(self):
        return len(self._jobs)

    def get_full_config(self):
        config = {}
        for job in self._jobs:
            config[job.name] = job.config
        return config

    def get_custom_config(self):
        return self._custom_config

    def _get_job_by_name(self, key):
        for job in self._jobs:
            if job.name == key:
                return job
        raise KeyError('No job found with a given name.')

    def _get_job_by_tag(self, key):
        for job in self._jobs:
            if job.tag == key:
                return job
        raise KeyError('No job found with a given tag.')

    def _get_job_by_number(self, key):
        for job in self._jobs:
            if job.number == key:
                return job
        raise KeyError('No job found with a given number.')

    def print_summary(self):
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
        table = Utils.make_table(('#', 'JOB NAME', 'OUTCOME', 'DURATION'), rows, ('r', 'l', 'c', 'c'))
        self._logger.info('\n\n'+table+'\n')

    def print_logs(self):
        for job in self:
            if len(job.logs) > 0:
                self._logger.info(job.name+' LOGS:\n'+'\n'.join(job.logs)+'\n')

    def filter_jobs(self, included_jobs):
        self._jobs = [job for job in self if job.number in included_jobs]

    def set_custom_config(self, config):
        for job_name, job_config in config.iteritems():
            job = self[job_name]
            job.set_config(job_config)
        self._custom_config = config
