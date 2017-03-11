import os
import logging
from Explorer import build_explorer

class DependencyChecker(object):
    @staticmethod
    def instance():
        return DependencyChecker._instance

    @staticmethod
    def is_active():
        return DependencyChecker._instance

    @staticmethod
    def notify(path):
        if DependencyChecker.is_active():
            DependencyChecker._instance._requested_paths.add(path)

    @staticmethod
    def is_ok(verbose=True):
        logger = logging.getLogger(__name__)
        instance = DependencyChecker._instance
        unexpected = instance._requested_paths - instance._expected_paths
        missing = instance._expected_paths - instance._requested_paths
        if verbose:
            for path in unexpected:
                logger.warning("Unspecified dependency of '{}': on {}".format(instance._job_name, path))
            for path in missing:
                logger.warning("Unnecessary dependency of '{}': on {}".format(instance._job_name, path))
        return len(missing) == 0 and len(unexpected) == 0

    def __init__(self, job_name, dependencies):
        self._job_name = job_name
        self._expected_paths = set(dependencies)
        self._requested_paths = set()

    def __enter__(self):
        logger = logging.getLogger(__name__)
        if DependencyChecker.is_active():
            logger.warning('Activating a new dependency checker while another is active!')
        DependencyChecker._instance = self
        return self

    def __exit__(self, _1, _2, _3):
        DependencyChecker._instance = None

    _instance = None

class CompletionGuard(object):
    def __init__(self, files):
        self._files = files
        self._completed = False

    def __enter__(self):
        self._completed = False
        return self

    def __exit__(self, _1, _2, _3):
        if not self._completed:
            for f in self._files:
                if os.path.isfile(f):
                    os.remove(f)

    def complete(self):
        self._completed = True

def exists(path, base=None):
    return os.path.exists(path(base))

def resolve(paths, base=None):
    resolved = []
    for p in paths:
        more = p(base=base) if callable(p) else p
        if isinstance(more, list):
            resolved.extend(more)
        else:
            resolved.append(more)

    return resolved

class Path(object):
    def __init__(self, path_string, parent=None):
        self._path_string = path_string
        self._parent = parent

    def __call__(self, base=None):
        base = base or build_explorer.get_last_build_dir()
        if self._parent:
            based_parent = self._parent._set_base(base)
            based = os.path.join(based_parent, self._path_string)
        else:
            based = self._set_base(base)
        DependencyChecker.notify(based)
        return based

    def _set_base(self, base):
        base = base or ''
        return os.path.join(base, self._path_string)

class PathGroup(object):
    def __init__(self, paths):
        self._paths = paths

    def __call__(self, base=None):
        base = base or build_explorer.get_last_build_dir()
        paths = []
        for p in self._paths:
            if isinstance(p, PathGroup):
                paths.extend(p(base))
            else:
                paths.append(p(base))
        return paths
