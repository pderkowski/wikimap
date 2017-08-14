import inspect
import sys
import Embeddings
import TSNE
import NearestNeighbors
import ZoomIndexer
import Graph
from Evaluation import SimilarityEvaluator, TripletEvaluator
from Paths import AbstractPaths as P
from Builder.Job import Job


def get_jobs():
    module = sys.modules[__name__]
    return [
        obj()
        for _, obj
        in inspect.getmembers(module)
        if hasattr(obj, "__bases__") and Job in obj.__bases__]


class DownloadPagesDump(Job):
    def __init__(self):
        super(DownloadPagesDump, self).__init__(
            'DOWNLOAD PAGES DUMP',
            alias='dload_pages',
            inputs=[],
            outputs=[P.pages_dump])

        self.config = {
            'language': 'en'
        }

    def __call__(self):
        url = 'https://dumps.wikimedia.org/{}wiki/latest/{}wiki-latest-page.sql.gz'.format(
            self.config['language'],
            self.config['language'])
        self.data.download_pages_dump(url)


class DownloadLinksDump(Job):
    def __init__(self):
        super(DownloadLinksDump, self).__init__(
            'DOWNLOAD LINKS DUMP',
            alias='dload_links',
            inputs=[],
            outputs=[P.links_dump])

        self.config = {
            'language': 'en'
        }

    def __call__(self):
        url = 'https://dumps.wikimedia.org/{}wiki/latest/{}wiki-latest-pagelinks.sql.gz'.format(
            self.config['language'],
            self.config['language'])
        self.data.download_links_dump(url)


class DownloadCategoryLinksDump(Job):
    def __init__(self):
        super(DownloadCategoryLinksDump, self).__init__(
            'DOWNLOAD CATEGORY LINKS DUMP',
            alias='dload_clinks',
            inputs=[],
            outputs=[P.category_links_dump])

        self.config = {
            'language': 'en'
        }

    def __call__(self):
        url = 'https://dumps.wikimedia.org/{}wiki/latest/{}wiki-latest-categorylinks.sql.gz'.format(
            self.config['language'],
            self.config['language'])
        self.data.download_category_links_dump(url)


class DownloadPagePropertiesDump(Job):
    def __init__(self):
        super(DownloadPagePropertiesDump, self).__init__(
            'DOWNLOAD PAGE PROPERTIES DUMP',
            alias='dload_props',
            inputs=[],
            outputs=[P.page_properties_dump])

        self.config = {
            'language': 'en'
        }

    def __call__(self):
        url = 'https://dumps.wikimedia.org/{}wiki/latest/{}wiki-latest-page_props.sql.gz'.format(
            self.config['language'],
            self.config['language'])
        self.data.download_page_properties_dump(url)


class DownloadRedirectsDump(Job):
    def __init__(self):
        super(DownloadRedirectsDump, self).__init__(
            'DOWNLOAD REDIRECTS DUMP',
            alias='dload_reds',
            inputs=[],
            outputs=[P.redirects_dump])

        self.config = {
            'language': 'en'
        }

    def __call__(self):
        url = 'https://dumps.wikimedia.org/{}wiki/latest/{}wiki-latest-redirect.sql.gz'.format(
            self.config['language'],
            self.config['language'])
        self.data.download_redirects_dump(url)


class DownloadEvaluationDatasets(Job):
    def __init__(self):
        super(DownloadEvaluationDatasets, self).__init__(
            'DOWNLOAD EVALUATION DATASETS',
            alias='dload_eval',
            inputs=[],
            outputs=[P.evaluation_datasets])

        self.config = {}

    def __call__(self):
        url = 'https://www.dropbox.com/s/d61802lo5n3gdra/datasets.tar.gz?dl=1'
        self.data.download_evaluation_datasets(url)


class ImportPageTable(Job):
    def __init__(self):
        super(ImportPageTable, self).__init__(
            'IMPORT PAGE TABLE',
            alias='pages',
            inputs=[P.pages_dump],
            outputs=[P.pages])

    def __call__(self):
        pages = self.data.import_pages()
        self.data.set_pages(pages)


class ImportPagePropertiesTable(Job):
    def __init__(self):
        super(ImportPagePropertiesTable, self).__init__(
            'IMPORT PAGE PROPERTIES TABLE',
            alias='props',
            inputs=[P.page_properties_dump],
            outputs=[P.page_properties])

    def __call__(self):
        page_properties = self.data.import_page_properties()
        self.data.set_page_properties(page_properties)


class ImportCategoryLinksTable(Job):
    def __init__(self):
        super(ImportCategoryLinksTable, self).__init__(
            'IMPORT CATEGORY LINKS TABLE',
            alias='clinks',
            inputs=[P.category_links_dump, P.pages, P.page_properties],
            outputs=[P.category_links])

    def __call__(self):
        category_links = self.data.import_category_links()
        category_links = self.data.map_category_links_to_link_edges(
            category_links)
        category_links = self.data.filter_not_hidden_category_links(
            category_links)
        self.data.set_category_links(category_links)


class ImportRedirectsTable(Job):
    def __init__(self):
        super(ImportRedirectsTable, self).__init__(
            'IMPORT REDIRECTS TABLE',
            alias='reds',
            inputs=[P.redirects_dump],
            outputs=[P.redirects])

    def __call__(self):
        redirects = self.data.import_redirects()
        self.data.set_redirects(redirects)


class CreateLinkEdgesTable(Job):
    def __init__(self):
        super(CreateLinkEdgesTable, self).__init__(
            'CREATE LINK EDGES TABLE',
            alias='edges',
            inputs=[P.links_dump, P.pages],
            outputs=[P.link_edges])

    def __call__(self):
        links = self.data.import_links()
        links = self.data.map_links_to_link_edges(links)
        self.data.set_link_edges(links)


class ComputePagerank(Job):
    def __init__(self):
        super(ComputePagerank, self).__init__(
            'COMPUTE PAGERANK',
            alias='prank',
            inputs=[P.link_edges],
            outputs=[P.pagerank])

    def __call__(self):
        edges = self.data.get_link_edges()
        edges = self.data.filter_edges_by_node_count(edges, min_count=10)
        pagerank = Graph.pagerank(edges)
        self.data.set_pagerank(pagerank)


class ComputeEmbeddingsUsingLinks(Job):
    def __init__(self):
        super(ComputeEmbeddingsUsingLinks, self).__init__(
            'COMPUTE EMBEDDINGS',
            alias='embed',
            inputs=[P.link_edges, P.pagerank],
            outputs=[P.embeddings])

        self.config = {
            'method': Embeddings.DEFAULT_EMBEDDING_METHOD,
            'node_count': Embeddings.DEFAULT_EMBEDDING_NODE_COUNT,
            'dimension': Embeddings.DEFAULT_DIMENSION,
            'context_size': Embeddings.DEFAULT_CONTEXT_SIZE,
            'backtrack_probability': Embeddings.DEFAULT_BACKTRACK_PROBABILITY,
            'walks_per_node': Embeddings.DEFAULT_WALKS_PER_NODE,
            'dynamic_window': Embeddings.DEFAULT_DYNAMIC_WINDOW,
            'negative_samples': Embeddings.DEFAULT_NEGATIVE_SAMPLES,
            'epoch_count': Embeddings.DEFAULT_EPOCH_COUNT,
            'walk_length': Embeddings.DEFAULT_WALK_LENGTH,
            'categories': Embeddings.DEFAULT_USE_CATEGORIES
        }

    def __call__(self):
        data = self.data.get_link_edges()
        data = self.data.filter_edges_by_highest_pagerank(
            data,
            self.config['node_count'])

        if self.config['method'] == 'neighbor_list':
            data = self.data.get_link_lists(data)

        model = Embeddings.EmbeddingMethods(
            method=self.config['method'],
            dimension=self.config['dimension'],
            context_size=self.config['context_size'],
            backtrack_probability=self.config['backtrack_probability'],
            walks_per_node=self.config['walks_per_node'],
            epoch_count=self.config['epoch_count'],
            walk_length=self.config['walk_length'],
            negative_samples=self.config['negative_samples']
        )
        embeddings = model.train(data)

        self.data.set_embeddings(embeddings)

class ComputeEmbeddingsUsingLinksAndCategories(Job):
    def __init__(self):
        super(ComputeEmbeddingsUsingLinksAndCategories, self).__init__(
            'COMPUTE EMBEDDINGS',
            alias='embed',
            inputs=[P.link_edges, P.pagerank, P.category_links],
            outputs=[P.embeddings])

        self.config = {
            'method': Embeddings.DEFAULT_EMBEDDING_METHOD,
            'node_count': Embeddings.DEFAULT_EMBEDDING_NODE_COUNT,
            'dimension': Embeddings.DEFAULT_DIMENSION,
            'context_size': Embeddings.DEFAULT_CONTEXT_SIZE,
            'backtrack_probability': Embeddings.DEFAULT_BACKTRACK_PROBABILITY,
            'walks_per_node': Embeddings.DEFAULT_WALKS_PER_NODE,
            'dynamic_window': Embeddings.DEFAULT_DYNAMIC_WINDOW,
            'negative_samples': Embeddings.DEFAULT_NEGATIVE_SAMPLES,
            'epoch_count': Embeddings.DEFAULT_EPOCH_COUNT,
            'walk_length': Embeddings.DEFAULT_WALK_LENGTH,
            'categories': Embeddings.DEFAULT_USE_CATEGORIES
        }

    def __call__(self):
        edges = self.data.get_link_edges()
        edges = self.data.filter_edges_by_highest_pagerank(
            edges,
            self.config['node_count'])

        category_edges = self.data.get_edges_between_articles_and_categories()
        category_edges = self.data.filter_edges_by_highest_pagerank(
            category_edges,
            self.config['node_count'],
            endpoints='start')

        # Add links between articles and categories to normal links and then
        # inverse them and add them again to make a bidirectional connection.
        edges.extend(category_edges)
        category_edges.inverseEdges()
        edges.extend(category_edges)

        if self.config['method'] == 'neighbor_list':
            edges = self.data.get_link_lists(edges)

        model = Embeddings.EmbeddingMethods(
            method=self.config['method'],
            dimension=self.config['dimension'],
            context_size=self.config['context_size'],
            backtrack_probability=self.config['backtrack_probability'],
            walks_per_node=self.config['walks_per_node'],
            epoch_count=self.config['epoch_count'],
            walk_length=self.config['walk_length'],
            negative_samples=self.config['negative_samples']
        )
        embeddings = model.train(edges)

        self.data.set_embeddings(embeddings)

class CreateTitleIndex(Job):
    def __init__(self):
        super(CreateTitleIndex, self).__init__(
            'CREATE TITLE INDEX',
            alias='titles',
            inputs=[P.pages, P.category_links, P.redirects, P.embeddings],
            outputs=[P.title_index])

    def __call__(self):
        titles, ids = self.data.get_titles_ids_including_redirects_excluding_disambiguations()
        self.data.set_title_index(titles, ids)


class EvaluateEmbeddings(Job):
    def __init__(self):
        super(EvaluateEmbeddings, self).__init__(
            'EVALUATE EMBEDDINGS',
            alias='eval',
            inputs=[P.evaluation_datasets, P.embeddings, P.title_index],
            outputs=[P.evaluation_report])

    def __call__(self):
        embeddings = self.data.get_embeddings()
        evaluation_results = []
        evaluation_results.extend([
            SimilarityEvaluator(embeddings).evaluate(dataset)
            for dataset
            in self.data.get_similarity_datasets()
        ])
        evaluation_results.extend([
            TripletEvaluator(embeddings).evaluate(dataset)
            for dataset
            in self.data.get_triplet_datasets()
        ])
        self.data.set_evaluation_results(evaluation_results)
        self.logs.append(self.data.get_evaluation_results_as_table())


class ComputeTSNE(Job):
    def __init__(self):
        super(ComputeTSNE, self).__init__(
            'COMPUTE TSNE',
            alias='tsne',
            inputs=[P.embeddings, P.pagerank],
            outputs=[P.tsne])

        self.config = {
            'point_count': TSNE.DEFAULT_POINT_COUNT
        }

    def __call__(self):
        ids, embeddings = self.data.get_ids_embeddings_of_highest_ranked_points(self.config['point_count'])
        mappings = TSNE.train(embeddings)
        self.data.set_tsne_points(ids, mappings)


class ComputeHighDimensionalNeighbors(Job):
    def __init__(self):
        super(ComputeHighDimensionalNeighbors, self).__init__(
            'COMPUTE HIGH DIMENSIONAL NEIGHBORS',
            alias='hdnn',
            inputs=[P.embeddings, P.tsne, P.pages],
            outputs=[P.high_dimensional_neighbors])

        self.config = {
            'neighbors_count': NearestNeighbors.DEFAULT_NEAREST_NEIGHBORS_COUNT
        }

    def __call__(self):
        ids, titles, embeddings = self.data.get_ids_titles_embeddings_of_tsne_points()
        distances, indices = NearestNeighbors.computeNearestNeighbors(embeddings, self.config['neighbors_count'])
        self.data.set_high_dimensional_neighbors(ids, titles, indices, distances)


class ComputeLowDimensionalNeighbors(Job):
    def __init__(self):
        super(ComputeLowDimensionalNeighbors, self).__init__(
            'COMPUTE LOW DIMENSIONAL NEIGHBORS',
            alias='ldnn',
            inputs=[P.tsne, P.pages],
            outputs=[P.low_dimensional_neighbors])

        self.config = {
            'neighbors_count': NearestNeighbors.DEFAULT_NEAREST_NEIGHBORS_COUNT
        }

    def __call__(self):
        ids, titles, tsne_points = self.data.get_ids_titles_tsne_points()
        distances, indices = NearestNeighbors.computeNearestNeighbors(tsne_points, self.config['neighbors_count'])
        self.data.set_low_dimensional_neighbors(ids, titles, indices, distances)


class CreateAggregatedLinksTables(Job):
    def __init__(self):
        super(CreateAggregatedLinksTables, self).__init__(
            'CREATE AGGREGATED LINKS TABLES',
            alias='agg',
            inputs=[P.link_edges, P.tsne],
            outputs=[P.aggregated_inlinks, P.aggregated_outlinks])

    def __call__(self):
        ids = list(self.data.get_ids_of_tsne_points())
        outlinks = self.data.get_outlinks_of_points(ids)
        inlinks = self.data.get_inlinks_of_points(ids)
        self.data.set_outlinks(outlinks)
        self.data.set_inlinks(inlinks)


class CreateWikimapDatapointsTable(Job):
    def __init__(self):
        super(CreateWikimapDatapointsTable, self).__init__(
            'CREATE WIKIMAP DATAPOINTS TABLE',
            alias='points',
            inputs=[P.tsne, P.pages, P.high_dimensional_neighbors, P.low_dimensional_neighbors, P.pagerank],
            outputs=[P.wikimap_points])

    def __call__(self):
        points = self.data.get_wikimap_points()
        self.data.set_wikimap_points(points)


class CreateWikimapCategoriesTable(Job):
    def __init__(self):
        super(CreateWikimapCategoriesTable, self).__init__(
            'CREATE WIKIMAP CATEGORIES TABLE',
            alias='cats',
            inputs=[P.category_links, P.pages, P.tsne],
            outputs=[P.wikimap_categories])

        self.config = {
            'depth': Graph.DEFAULT_AGGREGATION_DEPTH
        }

    def __call__(self):
        category_id_page_id = self.data.get_reversed_edges_between_articles_and_categories_of_tsne_points()
        category_links = self.data.get_reversed_edges_between_categories()

        categories = Graph.aggregate(
            category_id_page_id,
            category_links,
            depth=self.config['depth'])

        self.data.set_wikimap_categories(categories.iteritems())

class CreateZoomIndex(Job):
    def __init__(self):
        super(CreateZoomIndex, self).__init__(
            'CREATE ZOOM INDEX',
            alias='zoom',
            inputs=[P.wikimap_points, P.pagerank],
            outputs=[P.zoom_index, P.wikimap_points, P.metadata])

        self.config = {
            'bucket_size': ZoomIndexer.DEFAULT_BUCKET_SIZE
        }

    def __call__(self):
        coords, ids = self.data.get_coords_ids_of_points()
        indexer = ZoomIndexer.Indexer(coords, ids, self.config['bucket_size'])
        self.data.set_zoom_index(indexer)
