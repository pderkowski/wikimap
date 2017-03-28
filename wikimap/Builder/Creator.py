import os
from .. import Utils
from ..Builds import Builds
from ..Paths import AbstractPaths as Paths
from Explorer import BuildExplorer
from Manager import BuildManager
from ArgumentParser import BuildArgumentParser

class BuildCreator(BuildExplorer):
    def __init__(self, builds_dir, build_prefix, base_build_index, language, target_jobs, forced_jobs, config):
        super(BuildCreator, self).__init__(builds_dir, build_prefix)

        self._base_build_index = base_build_index

        self._build = Builds[language]
        self._manager = BuildManager(self._build)

        parser = BuildArgumentParser(self._build)

        target_jobs = parser.parse_job_ranges(target_jobs)
        forced_jobs = parser.parse_job_ranges(forced_jobs)
        config = parser.parse_config(config)

        self._manager.plan(target_jobs, forced_jobs)
        self._manager.configure(config)

    def run(self):
        try:
            self._manager.run(prev_config=self._get_base_config(), prev_build_dir=self._get_base_build_dir(), new_build_dir=self._make_new_build_dir())
        finally:
            self._save_config(self._build.get_full_config())

    def get_build(self):
        return self._build

    def _get_base_build_dir(self):
        return self.get_build_dir(self._base_build_index or self._get_last_build_index())

    def _get_base_config(self):
        return self.get_config(self._base_build_index or self._get_last_build_index())

    def _get_new_build_index(self):
        last = self._get_last_build_index()
        return 0 if last is None else last + 1

    def _save_config(self, config):
        Utils.save_dict(Paths.config(self.get_last_build_dir()), config)

    def _make_new_build_dir(self):
        new_build_dir = os.path.join(self._builds_dir, self._build_prefix + str(self._get_new_build_index()))
        if not os.path.exists(self._builds_dir):
            os.makedirs(self._builds_dir)
        if not os.path.exists(new_build_dir):
            os.makedirs(new_build_dir)
        return new_build_dir
