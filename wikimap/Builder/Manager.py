import os
import logging
from Utils import make_links, format_duration
from ..Utils import Colors, color_text, make_table
from Job import Job
from Explorer import build_explorer

class BuildManager(object):
    def __init__(self, build, plan):
        self._logger = logging.getLogger(__name__)
        self._build = build
        self._included_jobs = plan[0]
        self._forced_jobs = plan[1]
        self._changed_files = set()
        self._summary = []
        self._previous_config = build_explorer.get_last_config()
        self._previous_build_dir = build_explorer.get_last_build_dir()
        self._new_config = build.get_config(self._included_jobs)
        self._new_build_dir = build_explorer.make_new_build_dir()

    def run(self):
        self._logger.info('STARTING BUILD IN {}'.format(self._new_build_dir))

        try:
            for job in self._build:
                if self._is_included(job):
                    if self._should_run(job):
                        self._run_job(job)
                    else:
                        self._skip_job(job)
        except KeyboardInterrupt:
            raise
        except Exception, e:
            self._logger.exception(str(e))
            raise
        finally:
            self._print_summary()
            build_explorer.save_config(self._new_config)

    def _run_job(self, job):
        self._logger.info('STARTING JOB: {}'.format(job.name))
        try:
            self._changed_files.update(job.outputs())
            job.run()
        finally:
            self._summary.append((job.number, job.outcome, job.name, job.duration))

    def _skip_job(self, job):
        self._logger.info('SKIPPING JOB: {}'.format(job.name))
        try:
            job.skip()
            make_links(zip(job.outputs(base=self._previous_build_dir), job.outputs()))
        finally:
            self._summary.append((job.number, job.outcome, job.name, job.duration))

    def _is_included(self, job):
        return self._included_jobs[job.number]

    def _should_run(self, job):
        return self._is_forced(job)\
            or self._inputs_changed(job)\
            or self._config_changed(job)\
            or not self._outputs_computed(job)

    def _is_forced(self, job):
        return self._forced_jobs[job.number]

    def _outputs_computed(self, job):
        return self._previous_build_dir and all(os.path.exists(o) for o in job.outputs(base=self._previous_build_dir))

    def _inputs_changed(self, job):
        return any(input_ in self._changed_files for input_ in job.inputs())

    def _config_changed(self, job):
        previous_build_config = self._previous_config.get(job.name, {})
        current_build_config = job.config
        return previous_build_config != current_build_config

    def _print_summary(self):
        outcome_2_color = {
            Job.SUCCESS: Colors.GREEN,
            Job.FAILURE: Colors.RED,
            Job.SKIPPED: Colors.BLUE,
            Job.ABORTED: Colors.YELLOW,
            Job.WARNING: Colors.YELLOW
        }

        rows = [(str(number), name, color_text('[{}]'.format(outcome), outcome_2_color[outcome]), format_duration(duration)) for (number, outcome, name, duration) in self._summary]
        table = make_table(('#', 'JOB NAME', 'OUTCOME', 'DURATION'), ('r', 'l', 'c', 'c'), rows)
        self._logger.info('\n\n'+table.get_string()+'\n')
