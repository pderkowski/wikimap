import Tables
import shelve
import Utils
import Paths
import DataHelpers as Helpers
from common.Zoom import ZoomIndex
from common.Terms import TermIndex
from DataHelpers import pipe, ColumnIt, LogIt, NotEqualIt, GroupIt, NotInIt, FlipIt
from itertools import imap, izip, repeat

def download_pages_dump(url):
    Utils.download(url, Paths.pages_dump())

def download_links_dump(url):
    Utils.download(url, Paths.links_dump())

def download_category_links_dump(url):
    Utils.download(url, Paths.category_links_dump())

def download_page_properties_dump(url):
    Utils.download(url, Paths.page_properties_dump())

def download_redirects_dump(url):
    Utils.download(url, Paths.redirects_dump())

def download_evaluation_datasets(url):
    Utils.download_and_extract(url, Paths.evaluation_datasets_dir())

def import_pages():
    return Tables.Import.PageTable(Paths.pages_dump()).read()

def import_links():
    return Tables.Import.LinksTable(Paths.links_dump()).read()

def import_category_links():
    return Tables.Import.CategoryLinksTable(Paths.category_links_dump()).read()

def import_page_properties():
    return Tables.Import.PagePropertiesTable(Paths.page_properties_dump()).read()

def import_redirects():
    return Tables.Import.RedirectsTable(Paths.redirects_dump()).read()

def get_hidden_categories():
    joined_table = Tables.Join(Paths.pages(), Paths.page_properties())
    return frozenset(ColumnIt(0)(joined_table.selectHiddenCategories()))

def get_link_edges():
    joined_table = Tables.Join(Paths.pages(), Paths.links())
    return joined_table.selectLinkEdges()

def get_link_edges_as_strings():
    edge_table = Tables.EdgeTable(Paths.link_edges(), stringify=True)
    return edge_table

def get_ids_of_articles():
    pages_table = Tables.PageTable(Paths.pages())
    return ColumnIt(0)(pages_table.select_id_of_articles())

def get_ids_of_embeddings():
    embeddings_table = Tables.EmbeddingsTable(Paths.embeddings())
    return embeddings_table.keys()

def get_redirects():
    joined_table = Tables.Join(Paths.redirects(), Paths.pages())
    return joined_table.selectRedirectEdges()

def get_link_edges_between_highest_ranked_nodes(node_count):
    edges_table = Tables.EdgeTable(Paths.link_edges())
    pagerank_table = Tables.PagerankTable(Paths.pagerank())
    ids = list(ColumnIt(0)(pagerank_table.selectIdsByDescendingRank(node_count)))
    edges_table.filterByNodes(ids)
    return LogIt(1000000, start="Reading edges...")(edges_table)

def get_titles_ids_including_redirects():
    ids_of_articles = get_ids_of_embeddings()
    redirects = get_redirects()
    id2id = dict((i, i) for i in ids_of_articles)
    for (i, redirect) in redirects:
        id2id[i] = redirect
    ids, titles = get_ids_titles()
    ids_of_embeddings = set(get_ids_of_embeddings())
    title2id = dict((t, id2id[i]) for (t, i) in izip(titles, ids) if i in ids_of_embeddings)
    return ColumnIt(0)(title2id.iteritems()), ColumnIt(1)(title2id.iteritems())

def get_ids_titles():
    pages_table = Tables.PageTable(Paths.pages())
    ids_titles = list(pages_table.select_id_title_of_articles())
    return ColumnIt(0)(ids_titles), ColumnIt(1)(ids_titles)

def get_ids_embeddings_of_highest_ranked_points(point_count):
    pagerank_table = Tables.PagerankTable(Paths.pagerank())
    ids = pipe(pagerank_table.selectIdsByDescendingRank(point_count), ColumnIt(0), list)
    embeddings_table = Tables.EmbeddingsTable(Paths.embeddings())
    embeddings = imap(embeddings_table.get, ids)
    return ids, embeddings

def get_ids_titles_embeddings_of_tsne_points():
    joined_table = Tables.Join(Paths.tsne(), Paths.pages())
    data = list(joined_table.select_id_title_tsneX_tsneY())
    ids, titles = list(ColumnIt(0)(data)), list(ColumnIt(1)(data))
    embeddings_table = Tables.EmbeddingsTable(Paths.embeddings())
    embeddings = imap(embeddings_table.get, ids)
    return ids, titles, embeddings

def get_ids_titles_tsne_points():
    joined_table = Tables.Join(Paths.tsne(), Paths.pages())
    data = list(joined_table.select_id_title_tsneX_tsneY())
    ids, titles, points = list(ColumnIt(0)(data)), list(ColumnIt(1)(data)), ColumnIt(2, 3)(data)
    return ids, titles, points

def get_ids_of_tsne_points():
    tsne_table = Tables.TSNETable(Paths.tsne())
    return ColumnIt(0)(tsne_table.selectAll())

def get_outlinks_of_points(ids):
    edges_table = Tables.EdgeTable(Paths.link_edges())
    edges_table.filterByNodes(ids)
    edges_table.sortByStartNode()
    return edges_table

def get_inlinks_of_points(ids):
    edges_table = Tables.EdgeTable(Paths.link_edges())
    edges_table.filterByNodes(ids)
    edges_table.inverseEdges()
    edges_table.sortByStartNode()
    return edges_table

def get_wikimap_points():
    joined_table = Tables.Join(Paths.tsne(), Paths.pages(), Paths.high_dimensional_neighbors(), Paths.low_dimensional_neighbors(), Paths.pagerank())
    return joined_table.selectWikimapPoints()

def get_ids_category_names_of_tsne_points():
    joined_table = Tables.Join(Paths.category_links(), Paths.tsne())
    return joined_table.select_id_category()

def get_edges_between_categories():
    joined_table = Tables.Join(Paths.category_links(), Paths.pages())
    return joined_table.selectCategoryLinks()

def get_coords_ids_of_points():
    joined_table = Tables.Join(Paths.wikimap_points(), Paths.pagerank())
    data = list(joined_table.select_id_x_y_byRank())
    return ColumnIt(1, 2)(data), ColumnIt(0)(data)

def get_terms():
    wikipoints_table = Tables.WikimapPointsTable(Paths.wikimap_points())
    categories_table = Tables.WikimapCategoriesTable(Paths.wikimap_categories())
    return ColumnIt(0)(wikipoints_table.selectTitles()), ColumnIt(0)(categories_table.selectTitles())

def get_wordsim353_dataset():
    return Tables.EvaluationDataset(Paths.wordsim353_all())

def get_title_index():
    return Tables.TitleIndex(Paths.title_index())

def get_indexed_embeddings():
    return Tables.IndexedEmbeddingsTable(Paths.embeddings(), Paths.title_index())

def set_pages(pages):
    pages_table = Tables.PageTable(Paths.pages())
    pages_table.create()
    pages_table.populate(LogIt(1000000)(pages))

def set_links(links):
    links_table = Tables.LinksTable(Paths.links())
    links_table.create()
    links_table.populate(LogIt(1000000)(links))

def set_category_links(category_links, hidden_categories):
    category_links_table = Tables.CategoryLinksTable(Paths.category_links())
    category_links_table.create()
    category_links_table.populate(pipe(category_links, NotInIt(hidden_categories, 1), LogIt(1000000)))

def set_page_properties(page_properties):
    page_properties_table = Tables.PagePropertiesTable(Paths.page_properties())
    page_properties_table.create()
    page_properties_table.populate(LogIt(1000000)(page_properties))

def set_redirects(redirects):
    redirects_table = Tables.RedirectsTable(Paths.redirects())
    redirects_table.create()
    redirects_table.populate(LogIt(1000000)(redirects))

def set_link_edges(edges):
    edges_table = Tables.EdgeTable(Paths.link_edges())
    edges_table.populate(LogIt(1000000)(edges))

def set_pagerank(pagerank):
    pagerank_table = Tables.PagerankTable(Paths.pagerank())
    pagerank_table.create()
    pagerank_table.populate(pagerank)

def set_embeddings(embeddings):
    embeddings_table = Tables.EmbeddingsTable(Paths.embeddings())
    embeddings_table.create(embeddings)

def set_title_index(titles, ids):
    title_index = Tables.TitleIndex(Paths.title_index())
    title_index.create(izip(imap(Helpers.normalize_word, titles), ids))

def set_tsne_points(ids, mappings):
    tsne_table = Tables.TSNETable(Paths.tsne())
    tsne_table.create()
    tsne_table.populate(izip(ids, mappings[:, 0], mappings[:, 1]))

def set_high_dimensional_neighbors(ids, titles, indices, distances):
    hdn_table = Tables.HighDimensionalNeighborsTable(Paths.high_dimensional_neighbors())
    hdn_table.create()
    hdn_table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

def set_low_dimensional_neighbors(ids, titles, indices, distances):
    ldn_table = Tables.LowDimensionalNeighborsTable(Paths.low_dimensional_neighbors())
    ldn_table.create()
    ldn_table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

def set_outlinks(outlinks):
    outlinks_table = Tables.AggregatedLinksTable(Paths.aggregated_outlinks())
    outlinks_table.create(pipe(outlinks, LogIt(1000000), GroupIt))

def set_inlinks(inlinks):
    inlinks_table = Tables.AggregatedLinksTable(Paths.aggregated_inlinks())
    inlinks_table.create(pipe(inlinks, LogIt(1000000), GroupIt))

def set_wikimap_points(points):
    wikimap_points_table = Tables.WikimapPointsTable(Paths.wikimap_points())
    wikimap_points_table.create()
    wikimap_points_table.populate(points)

def set_wikimap_categories(categories):
    category_table = Tables.WikimapCategoriesTable(Paths.wikimap_categories())
    category_table.create()
    category_table.populate(pipe(categories, NotEqualIt([], 1), LogIt(100000)))

def set_zoom_index(indexer):
    zoom_index = ZoomIndex(Paths.zoom_index())
    zoom_index.build(indexer.index2data())
    wikipoints_table = Tables.WikimapPointsTable(Paths.wikimap_points())
    wikipoints_table.updateIndex(FlipIt(indexer.data2index()))
    metadata_table = shelve.open(Paths.metadata())
    metadata_table['bounds'] = indexer.getBounds()
    metadata_table.close()

def set_term_index(wikipoint_titles, category_titles):
    term_index = TermIndex(Paths.term_index())
    term_index.add(izip(wikipoint_titles, repeat(False)))
    term_index.add(izip(category_titles, repeat(True)))
