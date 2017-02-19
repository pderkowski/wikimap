import os

class PathGetter(object):
    def __init__(self, paths, name):
        self._paths = paths
        self._name = name

    def __call__(self, base=None):
        return self._paths._get(self._name, base=base)

class PathBase(object):
    def __init__(self):
        self._files = {}
        self.base = ""

    def add(self, files):
        for k, v in files.iteritems():
            self._files[k] = v

    def __getitem__(self, key):
        return PathGetter(self, key)

    def _get(self, key, base=None):
        if not base:
            base = self.base

        if isinstance(self._files[key], list):
            return [os.path.join(base, v) for v in self._files[key]]
        else:
            return os.path.join(base, self._files[key])

def resolvePaths(paths_, base=None):
    resolved = []
    for p in paths_:
        more = p(base=base) if callable(p) else p
        if isinstance(more, list):
            resolved.extend(more)
        else:
            resolved.append(more)

    return resolved
