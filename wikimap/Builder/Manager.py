import sys
import os
from Planner import BuildPlanner
from .. import Utils
from Config import BuildConfig
from ..Paths import AbstractPaths as Paths


class BuildManager(object):
    def __init__(self, jobs, target_jobs, forced_jobs):
        self._logger = Utils.get_logger(__name__)
        self._build = BuildPlanner(jobs).plan(target_jobs, forced_jobs)

    def configure(self, config):
        for job in self._build:
            job_config = config.get_job_config(job.alias)
            job.configure(job_config)

    def run(self, prev_config, prev_build_dir, new_build_dir):
        new_config = BuildConfig.from_build(self._build)
        BuildRunner(self._build, prev_config, prev_build_dir, new_build_dir, new_config).run()

    def print_jobs(self):
        self._logger.info('\n\n'+self._build.get_job_list_str()+'\n')

    def print_config(self):
        self._logger.info('\n\n'+str(BuildConfig.from_build(self._build))+'\n')


class BuildRunner(object):
    def __init__(self, build, prev_config, prev_build_dir, new_build_dir, new_config):
        self._logger = Utils.get_logger(__name__)
        self._build = build
        self._prev_config = prev_config
        self._prev_build_dir = prev_build_dir
        self._new_build_dir = new_build_dir
        self._new_config = new_config
        self._changed_files = set()

    def run(self):
        self._logger.important('STARTING BUILD IN {}'.format(self._new_build_dir))
        self._logger.info('BUILD CONFIG:\n{}'.format(self._new_config))
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
            self._new_config.save(Paths.config(self._new_build_dir))
            self._logger.info('\n\n'+self._build.get_summary_str()+'\n')
            self._print_job_logs()

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
        previous_build_config = self._prev_config.get_job_config(job.alias)
        current_build_config = self._new_config.get_job_config(job.alias)
        return previous_build_config != current_build_config

    def _log_job_action(self, job_action, job_build_order, job_name):
        format_str = '{{}} JOB [{{:{}}}/{{}}]: {{}}'.format(Utils.get_number_width(len(self._build)))
        self._logger.important(format_str.format(job_action, (job_build_order + 1), len(self._build), job_name))

    def _print_job_logs(self):
        for job in self._build:
            if len(job.logs) > 0:
                self._logger.info(job.name+' LOGS:\n'+'\n'.join(job.logs)+'\n')
