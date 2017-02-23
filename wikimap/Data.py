import Tables
import shelve
from common.Zoom import ZoomIndex
from common.Terms import TermIndex
from Utils import pipe, ColumnIt, LogIt, NotEqualIt, GroupIt, NotInIt, FlipIt
from itertools import imap, izip, repeat

def import_category_links(category_links_dump_path):
    return Tables.Import.CategoryLinksTable(category_links_dump_path).read()

def import_page_properties(page_properties_dump_path):
    return Tables.Import.PagePropertiesTable(page_properties_dump_path).read()

def import_links(links_dump_path):
    return Tables.Import.LinksTable(links_dump_path).read()

def import_pages(pages_dump_path):
    return Tables.Import.PageTable(pages_dump_path).read()

def import_redirects(redirects_dump_path):
    return Tables.Import.RedirectsTable(redirects_dump_path).read()

def get_ids_titles_embeddings_of_tsne_points(embeddings_path, tsne_path, pages_path):
    joined_table = Tables.Join(tsne_path, pages_path)
    data = list(joined_table.select_id_title_tsneX_tsneY())
    ids, titles = list(ColumnIt(0)(data)), list(ColumnIt(1)(data))
    embeddings_table = Tables.EmbeddingsTable(embeddings_path)
    embeddings = imap(embeddings_table.get, ids)
    return ids, titles, embeddings

def get_ids_titles_tsne_points(tsne_path, pages_path):
    joined_table = Tables.Join(tsne_path, pages_path)
    data = list(joined_table.select_id_title_tsneX_tsneY())
    ids, titles, points = list(ColumnIt(0)(data)), list(ColumnIt(1)(data)), ColumnIt(2, 3)(data)
    return ids, titles, points

def get_ids_embeddings_of_highest_ranked_points(embeddings_path, pagerank_path, point_count):
    pagerank_table = Tables.PagerankTable(pagerank_path)
    ids = pipe(pagerank_table.selectIdsByDescendingRank(point_count), ColumnIt(0), list)
    embeddings_table = Tables.EmbeddingsTable(embeddings_path)
    embeddings = imap(embeddings_table.get, ids)
    return ids, embeddings

def get_edges_as_strings(edges_path):
    edge_table = Tables.EdgeTable(edges_path, stringify=True)
    return edge_table

def get_edges_between_highest_ranked_nodes(edges_path, pagerank_path, node_count):
    edges_table = Tables.EdgeTable(edges_path)
    pagerank_table = Tables.PagerankTable(pagerank_path)
    ids = list(ColumnIt(0)(pagerank_table.selectIdsByDescendingRank(node_count)))
    edges_table.filterByNodes(ids)
    return LogIt(1000000, start="Reading edges...")(edges_table)

def get_ids_category_names_of_tsne_points(category_links_path, tsne_path):
    joined_table = Tables.Join(category_links_path, tsne_path)
    return joined_table.select_id_category()

def get_edges_between_categories(category_links_path, pages_path):
    joined_table = Tables.Join(category_links_path, pages_path)
    return joined_table.selectCategoryLinks()

def get_ids_of_tsne_points(tsne_path):
    tsne_table = Tables.TSNETable(tsne_path)
    return ColumnIt(0)(tsne_table.selectAll())

def get_outlinks_of_points(edges_path, ids):
    edges_table = Tables.EdgeTable(edges_path)
    edges_table.filterByNodes(ids)
    edges_table.sortByStartNode()
    return edges_table

def get_inlinks_of_points(edges_path, ids):
    edges_table = Tables.EdgeTable(edges_path)
    edges_table.filterByNodes(ids)
    edges_table.inverseEdges()
    edges_table.sortByStartNode()
    return edges_table

def get_wikimap_points(tsne_path, pages_path, hdn_path, ldn_path, pagerank_path):
    joined_table = Tables.Join(tsne_path, pages_path, hdn_path, ldn_path, pagerank_path)
    return joined_table.selectWikimapPoints()

def get_link_edges(links_path, pages_path):
    joined_table = Tables.Join(pages_path, links_path)
    return joined_table.selectLinkEdges()

def get_redirects(redirects_path, pages_path):
    joined_table = Tables.Join(redirects_path, pages_path)
    return joined_table.selectRedirectEdges()

def get_hidden_categories(pages_path, page_properties_path):
    joined_table = Tables.Join(pages_path, page_properties_path)
    return frozenset(ColumnIt(0)(joined_table.selectHiddenCategories()))

def get_coords_ids_of_points(wikipoints_path, pagerank_path):
    joined_table = Tables.Join(wikipoints_path, pagerank_path)
    data = list(joined_table.select_id_x_y_byRank())
    return ColumnIt(1, 2)(data), ColumnIt(0)(data)

def get_terms(wikipoints_path, wikicategories_path):
    wikipoints_table = Tables.WikimapPointsTable(wikipoints_path)
    categories_table = Tables.WikimapCategoriesTable(wikicategories_path)
    return ColumnIt(0)(wikipoints_table.selectTitles()), ColumnIt(0)(categories_table.selectTitles())

def get_disambiguations(link_edges_path, page_path, category_links_path, pagerank_path):
    joined_table = Tables.Join(page_path, category_links_path)
    pagerank_table = Tables.PagerankTable(pagerank_path)
    link_edges = Tables.EdgeTable(link_edges_path)

    ambiguous = ColumnIt(0)(joined_table.selectDisambiguationPages())
    link_edges.filterByStartNodes(ambiguous)
    disamb_candidates = link_edges.getEndNodes()
    rank_of_candidates = dict(pagerank_table.select_id_rank(disamb_candidates))
    link_edges.sortByStartNode()

    return [(s, max(ends, key=rank_of_candidates.get)) for (s, ends) in GroupIt(link_edges)]

def get_article_ids(pages_path):
    pages_table = Tables.PageTable(pages_path)
    return ColumnIt(0)(pages_table.select_article_ids())

def get_ids_titles_of_embeddings(embeddings_path, pages_path):
    pages_table = Tables.PageTable(pages_path)
    embeddings_table = Tables.EmbeddingsTable(embeddings_path)
    embedded_pages = embeddings_table.keys()
    ids_titles = list(pages_table.select_id_title(embedded_pages))
    return ColumnIt(0)(ids_titles), ColumnIt(1)(ids_titles)

def get_article_mapping(article_mapping_path):
    return Tables.EdgeTable(article_mapping_path)

def set_high_dimensional_neighbors(ids, titles, indices, distances, output_path):
    hdn_table = Tables.HighDimensionalNeighborsTable(output_path)
    hdn_table.create()
    hdn_table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

def set_low_dimensional_neighbors(ids, titles, indices, distances, output_path):
    ldn_table = Tables.LowDimensionalNeighborsTable(output_path)
    ldn_table.create()
    ldn_table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

def set_tsne_points(ids, mappings, output_path):
    tsne_table = Tables.TSNETable(output_path)
    tsne_table.create()
    tsne_table.populate(izip(ids, mappings[:, 0], mappings[:, 1]))

def set_embeddings(embeddings, output_path):
    embeddings_table = Tables.EmbeddingsTable(output_path)
    embeddings_table.create(embeddings)

def set_pagerank(pagerank, output_path):
    pagerank_table = Tables.PagerankTable(output_path)
    pagerank_table.create()
    pagerank_table.populate(pagerank)

def set_categories(categories, output_path):
    category_table = Tables.WikimapCategoriesTable(output_path)
    category_table.create()
    category_table.populate(pipe(categories, NotEqualIt([], 1), LogIt(100000)))

def set_outlinks(outlinks, output_path):
    outlinks_table = Tables.AggregatedLinksTable(output_path)
    outlinks_table.create(pipe(output_path, LogIt(1000000), GroupIt))

def set_inlinks(inlinks, output_path):
    inlinks_table = Tables.AggregatedLinksTable(output_path)
    inlinks_table.create(pipe(inlinks, LogIt(1000000), GroupIt))

def set_wikimap_points(points, output_path):
    wikimap_points_table = Tables.WikimapPointsTable(output_path)
    wikimap_points_table.create()
    wikimap_points_table.populate(points)

def set_edges(edges, output_path):
    edges_table = Tables.EdgeTable(output_path)
    edges_table.populate(LogIt(1000000)(edges))

def set_category_links(hidden_categories, category_links, output_path):
    category_links_table = Tables.CategoryLinksTable(output_path)
    category_links_table.create()
    category_links_table.populate(pipe(category_links, NotInIt(hidden_categories, 1), LogIt(1000000)))

def set_page_properties(page_properties, output_path):
    page_properties_table = Tables.PagePropertiesTable(output_path)
    page_properties_table.create()
    page_properties_table.populate(LogIt(1000000)(page_properties))

def set_links(links, output_path):
    links_table = Tables.LinksTable(output_path)
    links_table.create()
    links_table.populate(LogIt(1000000)(links))

def set_pages(pages, output_path):
    pages_table = Tables.PageTable(output_path)
    pages_table.create()
    pages_table.populate(LogIt(1000000)(pages))

def set_zoom_index(indexer, zoom_index_path, wikipoints_path, metadata_path):
    zoom_index = ZoomIndex(zoom_index_path)
    zoom_index.build(indexer.index2data())
    wikipoints_table = Tables.WikimapPointsTable(wikipoints_path)
    wikipoints_table.updateIndex(FlipIt(indexer.data2index()))
    metadata_table = shelve.open(metadata_path)
    metadata_table['bounds'] = indexer.getBounds()
    metadata_table.close()

def set_term_index(wikipoint_titles, category_titles, output_path):
    term_index = TermIndex(output_path)
    term_index.add(izip(wikipoint_titles, repeat(False)))
    term_index.add(izip(category_titles, repeat(True)))

def set_redirects(redirects, output_path):
    redirects_table = Tables.RedirectsTable(output_path)
    redirects_table.create()
    redirects_table.populate(LogIt(1000000)(redirects))

def set_article_mapping(article_ids, disambiguations, redirects, output_path):
    mapping = dict((id_, id_) for id_ in article_ids)
    for (id_, disambiguation) in disambiguations:
        mapping[id_] = disambiguation
    for (id_, redirect) in redirects:
        mapping[id_] = mapping[redirect] # if redirect points to an ambiguous page, redirect to its disambiguation
    edges_table = Tables.EdgeTable(output_path)
    edges_table.populate(LogIt(1000000)(mapping))

def set_title_index(ids, titles, article_mapping, output_path):
    titles_ids = izip(titles, ids)
    id2disambiguated = dict(article_mapping)
    embedding_index = Tables.EmbeddingIndex(output_path)
    embedding_index.create((t, id2disambiguated[i]) for (t, i) in titles_ids)
