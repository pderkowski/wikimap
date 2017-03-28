import os

class AbstractPath(object):
    def __init__(self, filename, parent=None):
        self._filename = filename
        self._parent = parent

    def __call__(self, base):
        base = self._parent(base) if self._parent else base
        return os.path.join(base, self._filename)

class AbstractPathGroup(object):
    def __init__(self, paths):
        self._paths = paths

    def __iter__(self):
        for path_or_group in self._paths:
            if isinstance(path_or_group, AbstractPathGroup):
                for path in path_or_group:
                    yield path
            else:
                yield path_or_group

    def __call__(self, base):
        return [path(base) for path in self]

    def __add__(self, other):
        return AbstractPathGroup(self._paths + other._paths)

class AbstractPaths(object):
    config = AbstractPath('config')
    pages_dump = AbstractPath('page.sql.gz')
    links_dump = AbstractPath('pagelinks.sql.gz')
    category_links_dump = AbstractPath('categorylinks.sql.gz')
    page_properties_dump = AbstractPath('page_props.sql.gz')
    redirects_dump = AbstractPath('redirect.sql.gz')
    pages = AbstractPath('pages.db')
    links = AbstractPath('links.db')
    category_links = AbstractPath('category_links.db')
    page_properties = AbstractPath('page_properties.db')
    redirects = AbstractPath('redirects.db')
    pagerank = AbstractPath('pagerank.db')
    tsne = AbstractPath('tsne.db')
    high_dimensional_neighbors = AbstractPath('hdnn.db')
    low_dimensional_neighbors = AbstractPath('ldnn.db')
    wikimap_points = AbstractPath('wikimap_points.db')
    wikimap_categories = AbstractPath('wikimap_categories.db')
    metadata = AbstractPath('metadata.db')
    zoom_index = AbstractPath('zoom_index.idx')
    link_edges = AbstractPath('link_edges.bin')
    embeddings = AbstractPath('embeddings.cdb')
    aggregated_inlinks = AbstractPath('aggregated_inlinks.cdb')
    aggregated_outlinks = AbstractPath('aggregated_outlinks.cdb')
    title_index = AbstractPath('title_index.idx')
    evaluation_report = AbstractPath('evaluation_report.csv')
    evaluation_datasets_dir = AbstractPath('evaluation_datasets')
    ws_353_all = AbstractPath('WS-353-ALL.txt', parent=evaluation_datasets_dir)
    ws_353_rel = AbstractPath('WS-353-REL.txt', parent=evaluation_datasets_dir)
    ws_353_sim = AbstractPath('WS-353-SIM.txt', parent=evaluation_datasets_dir)
    mc_30 = AbstractPath('MC-30.txt', parent=evaluation_datasets_dir)
    rg_65 = AbstractPath('RG-65.txt', parent=evaluation_datasets_dir)
    mturk_287 = AbstractPath('MTurk-287.txt', parent=evaluation_datasets_dir)
    simlex_999 = AbstractPath('SIMLEX-999.txt', parent=evaluation_datasets_dir)
    bless_rel_random = AbstractPath('BLESS-REL-RANDOM.txt', parent=evaluation_datasets_dir)
    bless_rel_mero = AbstractPath('BLESS-REL-MERO.txt', parent=evaluation_datasets_dir)
    evaluation_word_mapping = AbstractPath('word_mapping.txt', parent=evaluation_datasets_dir)
    evaluation_datasets = AbstractPathGroup([ws_353_all, ws_353_rel, ws_353_sim, mc_30, rg_65, mturk_287, simlex_999, bless_rel_random, bless_rel_mero])
    evaluation_files = AbstractPathGroup([evaluation_datasets, evaluation_word_mapping])

class ConcretePaths(object):
    def __init__(self, base):
        for (path_name, path_getter) in vars(AbstractPaths).iteritems():
            if not path_name.startswith('__'):
                setattr(self, path_name, path_getter(base))

class CheckedPaths(object):
    def __init__(self, base, expected_paths):
        self._paths = ConcretePaths(base)
        self._expected_paths = set(expected_paths)
        self._requested_paths = set()

        for (path_name, path_value) in vars(self._paths).iteritems():
            if not path_name.startswith('__'):
                setattr(CheckedPaths, path_name, self._make_property(path_name, path_value))

    def _make_property(self, path_name, path_value):
        def proxy_getter(self):
            self._notify(path_value)
            return path_value
        return property(proxy_getter)

    def _notify(self, path_or_paths):
        paths = path_or_paths if isinstance(path_or_paths, list) else [path_or_paths]
        for path in paths:
            self._requested_paths.add(path)

    def has_invalid_dependencies(self):
        unexpected, missing = self.get_invalid_dependencies()
        return unexpected or missing

    def get_invalid_dependencies(self):
        unexpected = self._requested_paths - self._expected_paths
        missing = self._expected_paths - self._requested_paths
        return unexpected, missing
