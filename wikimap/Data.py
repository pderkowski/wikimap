import Tables
import shelve
import Utils
import DataHelpers as Helpers
from common.Zoom import ZoomIndex
from DataHelpers import pipe, ColumnIt, LogIt, NotEqualIt, GroupIt, NotInIt, \
    FlipIt, InIt, LongerThanIt
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
        """Import pages table from compressed dump."""
        return Tables.Import.PageTable(self.P.pages_dump).read()

    def import_links(self):
        """Import links table from compressed dump."""
        return Tables.Import.LinksTable(self.P.links_dump).read()

    def import_category_links(self):
        """Import category links table from compressed dump."""
        return Tables.Import.CategoryLinksTable(
            self.P.category_links_dump
        ).read()

    def import_page_properties(self):
        """Import page properties table from compressed dump."""
        return Tables.Import.PagePropertiesTable(
            self.P.page_properties_dump
        ).read()

    def import_redirects(self):
        """Import redirects table from compressed dump."""
        return Tables.Import.RedirectsTable(self.P.redirects_dump).read()

    def select_hidden_categories(self):
        """Select hidden categories by joining other tables."""
        joined_table = Tables.Join(self.P.pages, self.P.page_properties)
        return frozenset(ColumnIt(0)(joined_table.select_hidden_categories()))

    def filter_not_hidden_category_links(self, category_links):
        """
        Remove irrelevant category links.

        Filter the category links so that mostly 'real' links remain. Hidden
        categories are used mainly for maintenance purposes, so they do not
        provide useful info.

        `category_links` links to filter.
        """
        hidden_categories = self.select_hidden_categories()
        return pipe(
            category_links,
            NotInIt(hidden_categories, 0),
            NotInIt(hidden_categories, 1))

    def get_article_title_2_id(self):
        """Get a dict mapping title to id for articles (namespace 0)."""
        pages_table = Tables.PageTable(self.P.pages)
        return dict(FlipIt(pages_table.select_id_title_of_articles()))

    def get_category_title_2_id(self):
        """Get a dict mapping title to id for categories (namespace 14)."""
        pages_table = Tables.PageTable(self.P.pages)
        return dict(FlipIt(pages_table.select_id_title_of_categories()))

    def map_links_to_link_edges(self, links):
        """
        Map tuples from dump to edges.

        Original links are tuples consisting of 4 fields:
        - id of a page where link originates
        - namespace of said page
        - title of a linked page
        - its namespace
        This function replaces it with simple (id_from, id_to) pairs that are
        easy to store and operate on.

        `links` - links in dump format
        """
        title_2_id = self.get_article_title_2_id()
        valid_links = pipe(links, ColumnIt(0, 2), InIt(title_2_id, 1))
        return imap(
            lambda (from_, to_): (from_, title_2_id[to_]),
            valid_links)

    def get_link_edges(self):
        """Get (load) the EdgeTable."""
        edge_table = Tables.EdgeTable(self.P.link_edges)
        return edge_table

    def filter_link_edges_by_node_count(self, edge_table, min_count=1):
        """
        Filter the EdgeTable.

        Filter the EdgeTable so that it only contains edges between nodes that
        occur at least the specified number of times.

        `edge_table` is an EdgeTable to filter

        `min_count` is a minimum number of times a node has to occur as an
        endpoint of an edge to be included in the returned table.
        """
        if min_count > 1:
            counts = edge_table.countNodes()
            edge_table.filterByNodes([
                n
                for (n, c)
                in counts.iteritems()
                if c >= min_count
            ])
        return edge_table

    def filter_link_edges_by_highest_pagerank(self, edge_table, node_count):
        """
        Filter the EdgeTable.

        Filter the EdgeTable so that only edges between highest ranked (by
        pagerank) nodes are left.

        `edge_table` is an EdgeTable to filter

        `node_count` is a number of highest ranked nodes to include
        """
        pagerank_table = Tables.PagerankTable(self.P.pagerank)
        ids = pipe(
            pagerank_table.select_ids_by_descending_rank(node_count),
            ColumnIt(0))
        edge_table.filterByNodes(ids)
        return edge_table

    def get_link_lists(self, edge_table):
        """
        Group links into link lists.

        Group links into link lists - one per node. Each link list is a list of
        neighbors (made by following outbound links). Only lists longer than 1
        are returned.

        `edge_table` is an EdgeTable containing links.
        """
        edge_table.sortByStartNode()
        return pipe(edge_table, GroupIt, ColumnIt(1), LongerThanIt(1))

    def get_ids_of_articles(self):
        pages_table = Tables.PageTable(self.P.pages)
        return ColumnIt(0)(pages_table.select_id_of_articles())

    def get_ids_of_embeddings(self):
        embeddings_table = Tables.EmbeddingsTable()
        embeddings_table.load(self.P.embeddings)
        return embeddings_table.words()

    def get_ids_of_disambiguations(self):
        joined_table = Tables.Join(self.P.pages, self.P.category_links)
        return ColumnIt(0)(joined_table.selectDisambiguationPages())

    def get_redirects(self):
        joined_table = Tables.Join(self.P.redirects, self.P.pages)
        return joined_table.selectRedirectEdges()

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
        ids = pipe(pagerank_table.select_ids_by_descending_rank(point_count), ColumnIt(0), list)
        embeddings_table = Tables.EmbeddingsTable()
        embeddings_table.load(self.P.embeddings)
        embeddings = imap(embeddings_table.__getitem__, ids)
        return ids, embeddings

    def get_ids_titles_embeddings_of_tsne_points(self):
        joined_table = Tables.Join(self.P.tsne, self.P.pages)
        data = list(joined_table.select_id_title_tsneX_tsneY())
        ids, titles = list(ColumnIt(0)(data)), list(ColumnIt(1)(data))
        embeddings_table = Tables.EmbeddingsTable()
        embeddings_table.load(self.P.embeddings)
        embeddings = imap(embeddings_table.__getitem__, ids)
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
        title_index = Tables.TitleIndex(self.P.title_index)

        def normalize_and_map_to_id(title):
            return title_index[Helpers.normalize_word(title)]

        return [
            Tables.SimilarityDataset('WS-353-ALL', self.P.ws_353_all,
                                     word1_col=1, word2_col=4, score_col=6),
            Tables.SimilarityDataset('WS-353-REL', self.P.ws_353_rel,
                                     word1_col=1, word2_col=4, score_col=6),
            Tables.SimilarityDataset('WS-353-SIM', self.P.ws_353_sim,
                                     word1_col=1, word2_col=4, score_col=6),
            Tables.SimilarityDataset('SIMLEX-999', self.P.simlex_999,
                                     word_mapper=normalize_and_map_to_id)
        ]

    def get_triplet_datasets(self):
        title_index = Tables.TitleIndex(self.P.title_index)

        def normalize_and_map_to_id(title):
            return title_index[Helpers.normalize_word(title)]

        return [
            Tables.TripletDataset('BLESS-REL-RANDOM', self.P.bless_rel_random,
                                  word_mapper=normalize_and_map_to_id),
            Tables.TripletDataset('BLESS-REL-MERO', self.P.bless_rel_mero,
                                  word_mapper=normalize_and_map_to_id),
            Tables.TripletDataset('WIKI-HAND', self.P.wiki_hand,
                                  word_mapper=normalize_and_map_to_id),
            Tables.TripletDataset('WIKI-GEN', self.P.wiki_gen,
                                  word_mapper=normalize_and_map_to_id)
        ]

    def get_embeddings(self):
        table = Tables.EmbeddingsTable()
        table.load(self.P.embeddings)
        return table

    def get_indexed_embeddings(self):
        return Tables.IndexedEmbeddingsTable(self.P.embeddings, self.P.title_index)

    def get_evaluation_results_as_table(self):
        return Tables.EvaluationReport(self.P.evaluation_report).get_pretty_table()

    def get_evaluation_scores(self):
        return Tables.EvaluationReport(self.P.evaluation_report).get_scores()

    def get_evaluation_test_names(self):
        return Tables.EvaluationReport(self.P.evaluation_report).get_test_names()

    def set_pages(self, pages):
        pages_table = Tables.PageTable(self.P.pages)
        pages_table.create()
        pages_table.populate(LogIt(1000000)(pages))

    def set_category_links(self, category_links):
        category_links_table = Tables.CategoryLinksTable(self.P.category_links)
        category_links_table.create()
        category_links_table.populate(LogIt(1000000)(category_links))

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
        pagerank_table.populate(
            imap(
                lambda (order, (page, rank)): (page, rank, order),
                enumerate(pagerank)
            )
        )

    def set_embeddings(self, embeddings):
        embeddings.save(self.P.embeddings)

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
