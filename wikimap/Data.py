import Tables
import shelve
import Utils
import DataHelpers as Helpers
from common.Zoom import ZoomIndex
from DataHelpers import pipe, ColumnIt, LogIt, NotEqualIt, GroupIt, NotInIt, FlipIt, InIt
from itertools import imap, izip

class Data(object):
    def __init__(self, paths):
        self.P = paths

    def download_pages_dump(self, url):
        Utils.download(url, self.P.pages_dump)

    def download_links_dump(self, url):
        Utils.download(url, self.P.links_dump)

    def download_category_links_dump(self, url):
        Utils.download(url, self.P.category_links_dump)

    def download_page_properties_dump(self, url):
        Utils.download(url, self.P.page_properties_dump)

    def download_redirects_dump(self, url):
        Utils.download(url, self.P.redirects_dump)

    def download_evaluation_datasets(self, url):
        Utils.download_and_extract(url, self.P.evaluation_datasets_dir)

    def import_pages(self):
        return Tables.Import.PageTable(self.P.pages_dump).read()

    def import_links(self):
        return Tables.Import.LinksTable(self.P.links_dump).read()

    def import_category_links(self):
        return Tables.Import.CategoryLinksTable(self.P.category_links_dump).read()

    def import_page_properties(self):
        return Tables.Import.PagePropertiesTable(self.P.page_properties_dump).read()

    def import_redirects(self):
        return Tables.Import.RedirectsTable(self.P.redirects_dump).read()

    def get_hidden_categories(self):
        joined_table = Tables.Join(self.P.pages, self.P.page_properties)
        return frozenset(ColumnIt(0)(joined_table.selectHiddenCategories()))

    def get_link_edges(self):
        joined_table = Tables.Join(self.P.pages, self.P.links)
        return joined_table.selectLinkEdges()

    def get_link_edges_as_strings(self):
        edge_table = Tables.EdgeTable(self.P.link_edges, stringify=True)
        return edge_table

    def get_ids_of_articles(self):
        pages_table = Tables.PageTable(self.P.pages)
        return ColumnIt(0)(pages_table.select_id_of_articles())

    def get_ids_of_embeddings(self):
        embeddings_table = Tables.EmbeddingsTable(self.P.embeddings)
        return embeddings_table.keys()

    def get_ids_of_disambiguations(self):
        joined_table = Tables.Join(self.P.pages, self.P.category_links)
        return ColumnIt(0)(joined_table.selectDisambiguationPages())

    def get_redirects(self):
        joined_table = Tables.Join(self.P.redirects, self.P.pages)
        return joined_table.selectRedirectEdges()

    def get_link_edges_between_highest_ranked_nodes(self, node_count):
        edges_table = Tables.EdgeTable(self.P.link_edges)
        pagerank_table = Tables.PagerankTable(self.P.pagerank)
        ids = list(ColumnIt(0)(pagerank_table.selectIdsByDescendingRank(node_count)))
        edges_table.filterByNodes(ids)
        return LogIt(1000000, start="Reading edges...")(edges_table)

    def get_id_2_redirected_id(self):
        ids_of_articles = self.get_ids_of_articles()
        redirects = self.get_redirects()
        id_2_id = dict((i, i) for i in ids_of_articles)
        for (i, redirect) in redirects:
            id_2_id[i] = redirect
        return id_2_id

    def get_titles_ids_including_redirects_excluding_disambiguations(self):
        id_2_redirected_id = self.get_id_2_redirected_id()
        title_2_id = dict((t, id_2_redirected_id[i]) for (i, t) in pipe(\
            izip(*self.get_ids_titles()),\
            InIt(set(self.get_ids_of_embeddings()), 0),\
            NotInIt(set(self.get_ids_of_disambiguations()), 0)))
        return ColumnIt(0)(title_2_id.iteritems()), ColumnIt(1)(title_2_id.iteritems())

    def get_ids_titles(self):
        pages_table = Tables.PageTable(self.P.pages)
        ids_titles = list(pages_table.select_id_title_of_articles())
        return ColumnIt(0)(ids_titles), ColumnIt(1)(ids_titles)

    def get_ids_embeddings_of_highest_ranked_points(self, point_count):
        pagerank_table = Tables.PagerankTable(self.P.pagerank)
        ids = pipe(pagerank_table.selectIdsByDescendingRank(point_count), ColumnIt(0), list)
        embeddings_table = Tables.EmbeddingsTable(self.P.embeddings)
        embeddings = imap(embeddings_table.get, ids)
        return ids, embeddings

    def get_ids_titles_embeddings_of_tsne_points(self):
        joined_table = Tables.Join(self.P.tsne, self.P.pages)
        data = list(joined_table.select_id_title_tsneX_tsneY())
        ids, titles = list(ColumnIt(0)(data)), list(ColumnIt(1)(data))
        embeddings_table = Tables.EmbeddingsTable(self.P.embeddings)
        embeddings = imap(embeddings_table.get, ids)
        return ids, titles, embeddings

    def get_ids_titles_tsne_points(self):
        joined_table = Tables.Join(self.P.tsne, self.P.pages)
        data = list(joined_table.select_id_title_tsneX_tsneY())
        ids, titles, points = list(ColumnIt(0)(data)), list(ColumnIt(1)(data)), ColumnIt(2, 3)(data)
        return ids, titles, points

    def get_ids_of_tsne_points(self):
        tsne_table = Tables.TSNETable(self.P.tsne)
        return ColumnIt(0)(tsne_table.selectAll())

    def get_outlinks_of_points(self, ids):
        edges_table = Tables.EdgeTable(self.P.link_edges)
        edges_table.filterByNodes(ids)
        edges_table.sortByStartNode()
        return edges_table

    def get_inlinks_of_points(self, ids):
        edges_table = Tables.EdgeTable(self.P.link_edges)
        edges_table.filterByNodes(ids)
        edges_table.inverseEdges()
        edges_table.sortByStartNode()
        return edges_table

    def get_wikimap_points(self):
        joined_table = Tables.Join(self.P.tsne, self.P.pages, self.P.high_dimensional_neighbors, self.P.low_dimensional_neighbors, self.P.pagerank)
        return joined_table.selectWikimapPoints()

    def get_ids_category_names_of_tsne_points(self):
        joined_table = Tables.Join(self.P.category_links, self.P.tsne)
        return joined_table.select_id_category()

    def get_edges_between_categories(self):
        joined_table = Tables.Join(self.P.category_links, self.P.pages)
        return joined_table.selectCategoryLinks()

    def get_coords_ids_of_points(self):
        joined_table = Tables.Join(self.P.wikimap_points, self.P.pagerank)
        data = list(joined_table.select_id_x_y_byRank())
        return ColumnIt(1, 2)(data), ColumnIt(0)(data)

    def get_similarity_datasets(self):
        return [Tables.SimilarityDataset('WS-353-ALL', self.P.ws_353_all),
            Tables.SimilarityDataset('WS-353-REL', self.P.ws_353_rel),
            Tables.SimilarityDataset('WS-353-SIM', self.P.ws_353_sim),
            Tables.SimilarityDataset('MC-30', self.P.mc_30),
            Tables.SimilarityDataset('RG-65', self.P.rg_65),
            Tables.SimilarityDataset('Mturk-287', self.P.mturk_287),
            Tables.SimilarityDataset('SIMLEX-999', self.P.simlex_999)]

    def get_relation_datasets(self):
        return [Tables.BlessRelationDataset('BLESS-REL-RANDOM', self.P.bless_rel_random),
            Tables.BlessRelationDataset('BLESS-REL-MERO', self.P.bless_rel_mero)]

    def get_title_index(self):
        return Tables.TitleIndex(self.P.title_index)

    def get_indexed_embeddings(self):
        return Tables.IndexedEmbeddingsTable(self.P.embeddings, self.P.title_index)

    def get_word_mapping(self):
        return Tables.WordMapping(self.P.evaluation_word_mapping)

    def get_evaluation_results_as_table(self):
        return Tables.EvaluationReport(self.P.evaluation_report).get_pretty_table()

    def get_evaluation_scores(self):
        return Tables.EvaluationReport(self.P.evaluation_report).get_evaluation_scores()

    def set_pages(self, pages):
        pages_table = Tables.PageTable(self.P.pages)
        pages_table.create()
        pages_table.populate(LogIt(1000000)(pages))

    def set_links(self, links):
        links_table = Tables.LinksTable(self.P.links)
        links_table.create()
        links_table.populate(LogIt(1000000)(links))

    def set_category_links(self, category_links, hidden_categories):
        category_links_table = Tables.CategoryLinksTable(self.P.category_links)
        category_links_table.create()
        category_links_table.populate(pipe(category_links, NotInIt(hidden_categories, 1), LogIt(1000000)))

    def set_page_properties(self, page_properties):
        page_properties_table = Tables.PagePropertiesTable(self.P.page_properties)
        page_properties_table.create()
        page_properties_table.populate(LogIt(1000000)(page_properties))

    def set_redirects(self, redirects):
        redirects_table = Tables.RedirectsTable(self.P.redirects)
        redirects_table.create()
        redirects_table.populate(LogIt(1000000)(redirects))

    def set_link_edges(self, edges):
        edges_table = Tables.EdgeTable(self.P.link_edges)
        edges_table.populate(LogIt(1000000)(edges))

    def set_pagerank(self, pagerank):
        pagerank_table = Tables.PagerankTable(self.P.pagerank)
        pagerank_table.create()
        pagerank_table.populate(pagerank)

    def set_embeddings(self, embeddings):
        embeddings_table = Tables.EmbeddingsTable(self.P.embeddings)
        embeddings_table.create(embeddings)

    def set_title_index(self, titles, ids):
        title_index = Tables.TitleIndex(self.P.title_index)
        title_index.create(izip(imap(Helpers.normalize_word, titles), ids))

    def set_tsne_points(self, ids, mappings):
        tsne_table = Tables.TSNETable(self.P.tsne)
        tsne_table.create()
        tsne_table.populate(izip(ids, mappings[:, 0], mappings[:, 1]))

    def set_high_dimensional_neighbors(self, ids, titles, indices, distances):
        hdn_table = Tables.HighDimensionalNeighborsTable(self.P.high_dimensional_neighbors)
        hdn_table.create()
        hdn_table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

    def set_low_dimensional_neighbors(self, ids, titles, indices, distances):
        ldn_table = Tables.LowDimensionalNeighborsTable(self.P.low_dimensional_neighbors)
        ldn_table.create()
        ldn_table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

    def set_outlinks(self, outlinks):
        outlinks_table = Tables.AggregatedLinksTable(self.P.aggregated_outlinks)
        outlinks_table.create(pipe(outlinks, LogIt(1000000), GroupIt))

    def set_inlinks(self, inlinks):
        inlinks_table = Tables.AggregatedLinksTable(self.P.aggregated_inlinks)
        inlinks_table.create(pipe(inlinks, LogIt(1000000), GroupIt))

    def set_wikimap_points(self, points):
        wikimap_points_table = Tables.WikimapPointsTable(self.P.wikimap_points)
        wikimap_points_table.create()
        wikimap_points_table.populate(points)

    def set_wikimap_categories(self, categories):
        category_table = Tables.WikimapCategoriesTable(self.P.wikimap_categories)
        category_table.create()
        category_table.populate(pipe(imap(lambda (title, ids): (title, ids, len(ids)), categories), NotEqualIt(0, 2), LogIt(100000)))

    def set_zoom_index(self, indexer):
        zoom_index = ZoomIndex(self.P.zoom_index)
        zoom_index.build(indexer.index2data())
        wikipoints_table = Tables.WikimapPointsTable(self.P.wikimap_points)
        wikipoints_table.updateIndex(FlipIt(indexer.data2index()))
        metadata_table = shelve.open(self.P.metadata)
        metadata_table['bounds'] = indexer.getBounds()
        metadata_table.close()

    def set_evaluation_results(self, results):
        evaluation_report = Tables.EvaluationReport(self.P.evaluation_report)
        evaluation_report.create(results)
