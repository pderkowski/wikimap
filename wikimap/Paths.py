import os

global_base = None

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

def set_base(path, base):
    if base:
        path = os.path.join(base, path)
    return path

def pages_dump(base=None):
    base = base or global_base
    return set_base('page.sql.gz', base=base)

def links_dump(base=None):
    base = base or global_base
    return set_base('pagelinks.sql.gz', base=base)

def category_links_dump(base=None):
    base = base or global_base
    return set_base('categorylinks.sql.gz', base=base)

def page_properties_dump(base=None):
    base = base or global_base
    return set_base('page_props.sql.gz', base=base)

def redirects_dump(base=None):
    base = base or global_base
    return set_base('redirect.sql.gz', base=base)

def pages(base=None):
    base = base or global_base
    return set_base('pages.db', base=base)

def links(base=None):
    base = base or global_base
    return set_base('links.db', base=base)

def category_links(base=None):
    base = base or global_base
    return set_base('category_links.db', base=base)

def page_properties(base=None):
    base = base or global_base
    return set_base('page_properties.db', base=base)

def redirects(base=None):
    base = base or global_base
    return set_base('redirects.db', base=base)

def pagerank(base=None):
    base = base or global_base
    return set_base('pagerank.db', base=base)

def tsne(base=None):
    base = base or global_base
    return set_base('tsne.db', base=base)

def high_dimensional_neighbors(base=None):
    base = base or global_base
    return set_base('hdnn.db', base=base)

def low_dimensional_neighbors(base=None):
    base = base or global_base
    return set_base('ldnn.db', base=base)

def wikimap_points(base=None):
    base = base or global_base
    return set_base('wikimap_points.db', base=base)

def wikimap_categories(base=None):
    base = base or global_base
    return set_base('wikimap_categories.db', base=base)

def metadata(base=None):
    base = base or global_base
    return set_base('metadata.db', base=base)

def zoom_index(base=None):
    base = base or global_base
    return set_base('zoom_index.idx', base=base)

def term_index(base=None):
    base = base or global_base
    return set_base('term_index.idx', base=base)

def link_edges(base=None):
    base = base or global_base
    return set_base('link_edges.bin', base=base)

def embeddings(base=None):
    base = base or global_base
    return set_base('embeddings.cdb', base=base)

def aggregated_inlinks(base=None):
    base = base or global_base
    return set_base('aggregated_inlinks.cdb', base=base)

def aggregated_outlinks(base=None):
    base = base or global_base
    return set_base('aggregated_outlinks.cdb', base=base)

def title_index(base=None):
    base = base or global_base
    return set_base('title_index.idx', base=base)

def evaluation_report(base=None):
    base = base or global_base
    return set_base('evaluation_report.csv', base=base)

def evaluation_datasets_dir(base=None):
    base = base or global_base
    return set_base('evaluation_datasets', base=base)

def ws_353_all(base=None):
    base = base or global_base
    return os.path.join(evaluation_datasets_dir(base), 'WS-353-ALL.txt')

def evaluation_word_mapping(base=None):
    base = base or global_base
    return os.path.join(evaluation_datasets_dir(base), 'word_mapping.txt')

def evaluation_datasets(base=None):
    base = base or global_base
    return [ws_353_all(base)]

def evaluation_files(base=None):
    base = base or global_base
    return evaluation_datasets(base) + [evaluation_word_mapping(base)]
