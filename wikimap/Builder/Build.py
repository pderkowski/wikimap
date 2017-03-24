from Planner import BuildPlanner
from itertools import izip
from Job import Properties, InvalidConfig

class Build(object):
    def __init__(self, jobs):
        self._custom_config = {}
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
                return self._get_job_by_tag(key)

    def __len__(self):
        return len(self._jobs)

    def plan(self, target_jobs, forced_jobs):
        forced_jobs = set(forced_jobs)
        target_jobs = set(target_jobs) | forced_jobs

        for job in forced_jobs:
            self[job].properties.append(Properties.Forced)

        planner = BuildPlanner(self)
        included_jobs_mask = planner.get_plan(target_jobs)
        self._jobs = [job for job, include in izip(self._jobs, included_jobs_mask) if include]

    def configure(self, config):
        if not isinstance(config, dict):
            raise InvalidConfig('Expected dict, got: {}'.format(type(config)))
        for job_name, job_config in config.iteritems():
            try:
                job = self._get_job_by_name(job_name)
                job.configure(job_config)
            except KeyError:
                raise InvalidConfig('No job {} in build.'.format(job_name))
            self._custom_config = config

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
