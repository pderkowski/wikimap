import sys
import os
from Planner import BuildPlanner
from .. import Utils
from pprint import pformat
from Job import Properties

class BuildManager(object):
    def __init__(self, build):
        self._build = build

    def plan(self, target_jobs, forced_jobs):
        forced_jobs = set(forced_jobs)
        target_jobs = set(target_jobs) | forced_jobs

        for job in forced_jobs:
            self._build[job].properties.append(Properties.Forced)

        planner = BuildPlanner(self._build)
        included_jobs = planner.get_included_jobs(target_jobs)
        self._build.filter_jobs(included_jobs)

    def configure(self, config):
        self._build.set_custom_config(config)

    def run(self, prev_config, prev_build_dir, new_build_dir):
        BuildRunner(self._build, prev_config, prev_build_dir, new_build_dir).run()

class BuildRunner(object):
    def __init__(self, build, prev_config, prev_build_dir, new_build_dir):
        self._logger = Utils.get_logger(__name__)
        self._build = build
        self._prev_config = prev_config
        self._prev_build_dir = prev_build_dir
        self._new_build_dir = new_build_dir
        self._changed_files = set()

    def run(self):
        self._logger.important('STARTING BUILD IN {}'.format(self._new_build_dir))
        self._logger.important('CUSTOM BUILD CONFIG:\n{}'.format(pformat(self._build.get_custom_config())))
        self._logger.info('FULL BUILD CONFIG:\n{}'.format(pformat(self._build.get_full_config())))
        self._logger.important(Utils.thin_line_separator)
        try:
            for i, job in enumerate(self._build):
                if self._should_run(job):
                    self._log_job_action('STARTING', i, job.name)
                    self._run_job(job)
                else:
                    self._log_job_action('SKIPPING', i, job.name)
                    self._skip_job(job)
        except KeyboardInterrupt:
            raise
        except Exception, e:
            self._logger.exception(str(e))
            raise
        except:
            self._logger.exception("Unexpected error: {}".format(sys.exc_info()[0]))
            raise
        finally:
            self._build.print_summary()
            self._build.print_logs()

    def _run_job(self, job):
        self._changed_files.update(job.outputs(self._new_build_dir))
        job.run(self._new_build_dir)

    def _skip_job(self, job):
        job.skip()
        Utils.make_links(zip(job.outputs(self._prev_build_dir), job.outputs(self._new_build_dir)))

    def _should_run(self, job):
        return job.is_forced()\
            or self._inputs_changed(job)\
            or self._config_changed(job)\
            or not self._outputs_computed(job)

    def _outputs_computed(self, job):
        return self._prev_build_dir and all(os.path.exists(o) for o in job.outputs(self._prev_build_dir))

    def _inputs_changed(self, job):
        return any(input_ in self._changed_files for input_ in job.inputs(self._new_build_dir))

    def _config_changed(self, job):
        previous_build_config = self._prev_config.get(job.name, {})
        current_build_config = job.config
        return previous_build_config != current_build_config

    def _log_job_action(self, job_action, job_build_order, job_name):
        format_str = '{{}} JOB [{{:{}}}/{{}}]: {{}}'.format(Utils.get_number_width(len(self._build)))
        self._logger.important(format_str.format(job_action, (job_build_order + 1), len(self._build), job_name))
