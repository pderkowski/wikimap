import os
from .. import Utils
from ..Paths import ConcretePaths as Paths
from ..Data import Data
from Config import BuildConfig

class BuildExplorer(object):
    def __init__(self, builds_dir, build_prefix):
        self._builds_dir = builds_dir
        self._build_prefix = build_prefix

    def get_build_name(self, build_index):
        return os.path.basename(self.get_build_dir(build_index))

    def get_build_dir(self, build_index):
        if build_index == -1:
            return self.get_last_build_dir()
        else:
            return os.path.join(self._builds_dir, self._build_prefix + str(build_index))

    def get_last_build_dir(self):
        return self.get_build_dir(self._get_last_build_index())

    def has_build_dir(self, build_index):
        return os.path.isdir(self.get_build_dir(build_index))

    def get_config(self, build_index):
        if self.has_build_dir(build_index):
            paths = self.get_paths(build_index)
            return BuildConfig.from_path(paths.config)
        else:
            return {}

    def get_data(self, build_index):
        return Data(self.get_paths(build_index))

    def get_paths(self, build_index):
        return Paths(self.get_build_dir(build_index))

    def _get_last_build_index(self):
        subdirs = Utils.get_subdirs(self._builds_dir)
        build_subdirs = [d for d in subdirs if d.startswith(self._build_prefix)]

        best_i, best_suffix = None, None
        for i, s in enumerate(build_subdirs):
            try:
                suffix = self._get_index_of_build(s)
                if best_suffix is None or suffix > best_suffix:
                    best_i = i
                    best_suffix = suffix
            except ValueError:
                pass

        if best_i is not None:
            return self._get_index_of_build(build_subdirs[best_i])
        else:
            return None

    def _get_index_of_build(self, build_dir):
        suffix = build_dir[len(self._build_prefix):]
        return int(suffix)
