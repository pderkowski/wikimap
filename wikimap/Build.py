import Jobs
import Builder


LANGUAGES = ['en', 'pl']
DEFAULT_LANGUAGE = 'en'
DEFAULT_TARGET_JOBS = 'all'
DEFAULT_FORCED_JOBS = ''
DEFAULT_SKIPPED_JOBS = ''


class Build(object):
    def __init__(self, builds_dir, build_prefix, base_build_index, target_jobs,
                 forced_jobs, skipped_jobs, config):

        self._explorer = Builder.BuildExplorer(builds_dir, build_prefix,
                                               base_build_index)

        if isinstance(config, basestring):
            build_config = Builder.BuildConfig.from_string(config)
        else:
            build_config = Builder.BuildConfig(config)

        jobs = self._get_jobs(build_config)

        if len(target_jobs) > 0 and target_jobs[0] == 'all':
            target_jobs = [j.alias for j in jobs]

        if len(forced_jobs) > 0 and forced_jobs[0] == 'all':
            forced_jobs = [j.alias for j in jobs]

        if len(skipped_jobs) > 0 and skipped_jobs[0] == 'all':
            skipped_jobs = [j.alias for j in jobs]

        self._manager = Builder.BuildManager(jobs, target_jobs, forced_jobs,
                                             skipped_jobs)

        for job in jobs:
            if 'language' in job.config:
                job.config['language'] = config['meta.language']

        self._manager.configure(build_config)

    def run(self):
        self._manager.run(prev_config=self._explorer.get_base_config(),
                          prev_build_dir=self._explorer.get_base_build_dir(),
                          new_build_dir=self._explorer.make_new_build_dir())

    def print_jobs(self):
        self._manager.print_jobs()

    def print_config(self):
        self._manager.print_config()

    def _get_jobs(self, config):
        jobs = Jobs.get_jobs()

        if config['embed.categories']:
            jobs = [j
                    for j in jobs
                    if not isinstance(j, Jobs.ComputeEmbeddingsUsingLinks)]
        else:
            jobs = [j
                    for j in jobs
                    if not isinstance(j, Jobs.ComputeEmbeddingsUsingLinksAndCategories)]

        return jobs
