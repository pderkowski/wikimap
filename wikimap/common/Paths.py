import os

class PathGetter(object):
    def __init__(self, paths, name):
        self._paths = paths
        self._name = name

    def __call__(self, base=None):
        return self._paths._get(self._name, base=base)

class Paths(object):
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

paths = Paths()
paths.add({
    'page'                      : 'page.db',
    'links'                     : 'links.db',
    'categoryLinks'             : 'categoryLinks.db',
    'pageProperties'            : 'pageProperties.db',
    'pagerank'                  : 'pagerank.db',
    'tsne'                      : 'tsne.db',
    'highDimensionalNeighbors'  : 'hdnn.db',
    'lowDimensionalNeighbors'   : 'ldnn.db',
    'wikimapPoints'             : 'wikimapPoints.db',
    'wikimapCategories'         : 'wikimapCategories.db',
    'metadata'                  : 'metadata.db',
    'zoomIndex'                 : 'zoom.idx',
    'termIndex'                 : 'term.idx',
    'pageSql'                   : 'page.sql.gz',
    'linksSql'                  : 'pagelinks.sql.gz',
    'categoryLinksSql'          : 'categorylinks.sql.gz',
    'pagePropertiesSql'         : 'pageprops.sql.gz',
    'edgeArray'                 : 'edgeArray',
    'aggregatedInlinks'         : 'aggregatedInlinks.cdb',
    'aggregatedOutlinks'        : 'aggregatedOutlinks.cdb',
    'embeddings'                : 'embeddings.cdb'
})

def resolve(paths_, base=None):
    resolved = []
    for p in paths_:
        more = p(base=base) if callable(p) else p
        if isinstance(more, list):
            resolved.extend(more)
        else:
            resolved.append(more)

    return resolved
