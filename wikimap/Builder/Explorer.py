import os
from .. import Utils

class BuildExplorer(object):
    def __init__(self):
        self._builds_dir = None
        self._build_prefix = None
        self._base_build_index = None

    def set_builds_dir(self, builds_dir, build_prefix):
        self._builds_dir = builds_dir
        self._build_prefix = build_prefix

    def set_base_build(self, build_index):
        self._base_build_index = build_index

    def make_new_build_dir(self):
        new_build_dir = os.path.join(self._builds_dir, self._build_prefix + str(self._get_new_build_index()))
        if not os.path.exists(self._builds_dir):
            os.makedirs(self._builds_dir)
        if not os.path.exists(new_build_dir):
            os.makedirs(new_build_dir)
        return new_build_dir

    def get_base_build_dir(self):
        return self._get_build_dir(self._base_build_index or self._get_last_build_index())

    def get_last_build_dir(self):
        return self._get_build_dir(self._get_last_build_index())

    def _get_build_dir(self, build_index):
        if build_index is not None:
            return os.path.join(self._builds_dir, self._build_prefix + str(build_index))
        else:
            return None

    def has_build_dir(self, build_index):
        return os.path.isdir(self._get_build_dir(build_index))

    def get_base_config(self):
        return self._get_config(self._base_build_index or self._get_last_build_index())

    def _get_config(self, build_index):
        build_dir = self._get_build_dir(build_index)
        if build_dir is not None:
            path = os.path.join(build_dir, 'config')
            if os.path.exists(path):
                return Utils.load_dict(path)
        return {}

    def save_config(self, config):
        path = os.path.join(self.get_last_build_dir(), 'config')
        Utils.save_dict(path, config)

    def _get_new_build_index(self):
        last = self._get_last_build_index()
        if last is None:
            return 0
        else:
            return last + 1

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

build_explorer = BuildExplorer()
