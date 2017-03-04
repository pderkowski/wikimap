import os

global_base = None

class ExpectedPaths(object):
    def __init__(self):
        self._expected = None
        self._got = None

    def set(self, paths):
        self._expected = set(paths)
        self._got = set()

    def clear(self):
        self._expected = None
        self._got = None

    def report(self):
        unexpected = self._got - self._expected
        missing = self._expected - self._got
        return (unexpected, missing)

    def check(self, path):
        if self._expected is not None:
            self._got.add(path)

expected_paths = ExpectedPaths()

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
        base = base or global_base
        if self._parent:
            based_parent = self._parent._set_base(base)
            based = os.path.join(based_parent, self._path_string)
        else:
            based = self._set_base(base)
        expected_paths.check(based)
        return based

    def _set_base(self, base):
        base = base or ''
        return os.path.join(base, self._path_string)

class PathGroup(object):
    def __init__(self, paths):
        self._paths = paths

    def __call__(self, base=None):
        base = base or global_base
        paths = []
        for p in self._paths:
            if isinstance(p, PathGroup):
                paths.extend(p(base))
            else:
                paths.append(p(base))
        return paths

pages_dump = Path('page.sql.gz')
links_dump = Path('pagelinks.sql.gz')
category_links_dump = Path('categorylinks.sql.gz')
page_properties_dump = Path('page_props.sql.gz')
redirects_dump = Path('redirect.sql.gz')
pages = Path('pages.db')
links = Path('links.db')
category_links = Path('category_links.db')
page_properties = Path('page_properties.db')
redirects = Path('redirects.db')
pagerank = Path('pagerank.db')
tsne = Path('tsne.db')
high_dimensional_neighbors = Path('hdnn.db')
low_dimensional_neighbors = Path('ldnn.db')
wikimap_points = Path('wikimap_points.db')
wikimap_categories = Path('wikimap_categories.db')
metadata = Path('metadata.db')
zoom_index = Path('zoom_index.idx')
term_index = Path('term_index.idx')
link_edges = Path('link_edges.bin')
embeddings = Path('embeddings.cdb')
aggregated_inlinks = Path('aggregated_inlinks.cdb')
aggregated_outlinks = Path('aggregated_outlinks.cdb')
title_index = Path('title_index.idx')
evaluation_report = Path('evaluation_report.csv')
evaluation_datasets_dir = Path('evaluation_datasets')
ws_353_all = Path('WS-353-ALL.txt', parent=evaluation_datasets_dir)
ws_353_rel = Path('WS-353-REL.txt', parent=evaluation_datasets_dir)
ws_353_sim = Path('WS-353-SIM.txt', parent=evaluation_datasets_dir)
mc_30 = Path('MC-30.txt', parent=evaluation_datasets_dir)
rg_65 = Path('RG-65.txt', parent=evaluation_datasets_dir)
mturk_287 = Path('MTurk-287.txt', parent=evaluation_datasets_dir)
simlex_999 = Path('SIMLEX-999.txt', parent=evaluation_datasets_dir)
evaluation_word_mapping = Path('word_mapping.txt', parent=evaluation_datasets_dir)
evaluation_datasets = PathGroup([ws_353_all, ws_353_rel, ws_353_sim, mc_30, rg_65, mturk_287, simlex_999])
evaluation_files = PathGroup([evaluation_datasets, evaluation_word_mapping])
