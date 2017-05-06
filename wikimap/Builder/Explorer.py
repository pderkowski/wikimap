import os
from ..Paths import ConcretePaths as Paths
from ..Data import Data
from Config import BuildConfig

class BuildExplorer(object):
    def __init__(self, builds_dir, build_prefix):
        self._builds_dir = builds_dir
        self._build_prefix = build_prefix

    def get_build_name(self, build):
        index = self._get_index_of_build(build)
        return os.path.basename(self.get_build_dir(index))

    def get_build_dir(self, build):
        index = self._get_index_of_build(build)
        return os.path.join(self._builds_dir, self._build_prefix + str(index))

    def has_build_dir(self, build):
        index = self._get_index_of_build(build)
        return os.path.isdir(self.get_build_dir(index))

    def get_config(self, build):
        index = self._get_index_of_build(build)
        paths = self.get_paths(index)
        return BuildConfig.from_path(paths.config)

    def get_data(self, build):
        index = self._get_index_of_build(build)
        return Data(self.get_paths(index))

    def get_paths(self, build):
        index = self._get_index_of_build(build)
        return Paths(self.get_build_dir(index))

    def _get_index_of_build(self, build):
        if isinstance(build, int):
            return build
        else:
            suffix = build[len(self._build_prefix):]
            return int(suffix)
