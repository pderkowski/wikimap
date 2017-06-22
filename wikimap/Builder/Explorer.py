import os
from ..Paths import ConcretePaths as Paths
from ..Data import Data
from .. import Utils
from Config import BuildConfig

class BuildExplorer(object):
    def __init__(self, builds_dir, build_prefix, base_build_index=-1):
        self._builds_dir = builds_dir
        self._build_prefix = build_prefix
        self._base_build_index = base_build_index

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

    def get_base_build_dir(self):
        if self._base_build_index == -1:
            index = self.get_last_build_index()
            if index is not None:
                return self.get_build_dir(index)
            else:
                return None
        else:
            if self.has_build_dir(self._base_build_index):
                return self.get_build_dir(self._base_build_index)
            else:
                return None

    def get_base_config(self):
        if self._base_build_index == -1:
            index = self.get_last_build_index()
            if index is not None:
                return self.get_config(index)
            else:
                return BuildConfig({})
        else:
            if self.has_build_dir(self._base_build_index):
                return self.get_config(self._base_build_index)
            else:
                return BuildConfig({})

    def get_new_build_index(self):
        last = self.get_last_build_index()
        return 0 if last is None else last + 1

    def get_last_build_index(self):
        try:
            subdirs = Utils.get_subdirs(self._builds_dir)
            build_subdirs = [d for d in subdirs
                             if d.startswith(self._build_prefix)]

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
        except OSError:
            return None

    def make_new_build_dir(self):
        new_build_dir = os.path.join(
            self._builds_dir,
            self._build_prefix + str(self.get_new_build_index()))
        if not os.path.exists(self._builds_dir):
            os.makedirs(self._builds_dir)
        if not os.path.exists(new_build_dir):
            os.makedirs(new_build_dir)
        return new_build_dir
