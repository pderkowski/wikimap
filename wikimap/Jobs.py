from Builder.Job import Job
from Embeddings import Embeddings
import TSNE
import NearestNeighbors
import ZoomIndexer
import Graph
from Evaluation import SimilarityEvaluator, TripletEvaluator
from Paths import AbstractPaths as P


class DownloadPagesDump(Job):
    def __init__(self, url):
        super(DownloadPagesDump, self).__init__(
            'DOWNLOAD PAGES DUMP',
            alias='dload_pages',
            inputs=[],
            outputs=[P.pages_dump])

        self.config = {
            'url': url
        }

    def __call__(self):
        self.data.download_pages_dump(self.config['url'])


class DownloadLinksDump(Job):
    def __init__(self, url):
        super(DownloadLinksDump, self).__init__(
            'DOWNLOAD LINKS DUMP',
            alias='dload_links',
            inputs=[],
            outputs=[P.links_dump])

        self.config = {
            'url': url
        }

    def __call__(self):
        self.data.download_links_dump(self.config['url'])


class DownloadCategoryLinksDump(Job):
    def __init__(self, url):
        super(DownloadCategoryLinksDump, self).__init__(
            'DOWNLOAD CATEGORY LINKS DUMP',
            alias='dload_clinks',
            inputs=[],
            outputs=[P.category_links_dump])

        self.config = {
            'url': url
        }

    def __call__(self):
        self.data.download_category_links_dump(self.config['url'])


class DownloadPagePropertiesDump(Job):
    def __init__(self, url):
        super(DownloadPagePropertiesDump, self).__init__(
            'DOWNLOAD PAGE PROPERTIES DUMP',
            alias='dload_props',
            inputs=[],
            outputs=[P.page_properties_dump])

        self.config = {
            'url': url
        }

    def __call__(self):
        self.data.download_page_properties_dump(self.config['url'])


class DownloadRedirectsDump(Job):
    def __init__(self, url):
        super(DownloadRedirectsDump, self).__init__(
            'DOWNLOAD REDIRECTS DUMP',
            alias='dload_reds',
            inputs=[],
            outputs=[P.redirects_dump])

        self.config = {
            'url': url
        }

    def __call__(self):
        self.data.download_redirects_dump(self.config['url'])


class DownloadEvaluationDatasets(Job):
    def __init__(self, url):
        super(DownloadEvaluationDatasets, self).__init__(
            'DOWNLOAD EVALUATION DATASETS',
            alias='dload_eval',
            inputs=[],
            outputs=[P.evaluation_datasets])

        self.config = {
            'url': url
        }

    def __call__(self):
        self.data.download_evaluation_datasets(self.config['url'])


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


class ImportLinksTable(Job):
    def __init__(self):
        super(ImportLinksTable, self).__init__(
            'IMPORT LINKS TABLE',
            alias='links',
            inputs=[P.links_dump],
            outputs=[P.links])

    def __call__(self):
        links = self.data.import_links()
        self.data.set_links(links)


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
        hidden_categories = self.data.get_hidden_categories()
        category_links = self.data.import_category_links()
        self.data.set_category_links(category_links, hidden_categories)


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
            inputs=[P.links, P.pages],
            outputs=[P.link_edges])

    def __call__(self):
        link_edges = self.data.select_link_edges()
        self.data.set_link_edges(link_edges)


class ComputePagerank(Job):
    def __init__(self):
        super(ComputePagerank, self).__init__(
            'COMPUTE PAGERANK',
            alias='prank',
            inputs=[P.link_edges],
            outputs=[P.pagerank])

    def __call__(self):
        edges = self.data.get_link_edges()
        pagerank = Graph.pagerank(edges)
        self.data.set_pagerank(pagerank)


class ComputeEmbeddings(Job):
    def __init__(self):
        super(ComputeEmbeddings, self).__init__(
            'COMPUTE EMBEDDINGS',
            alias='embed',
            inputs=[P.link_edges, P.pagerank],
            outputs=[P.embeddings])

        self.config = {
            'method': 'node2vec',
            'node_count': 1000000,
            'dimensions': 128,
            'context_size': 10,
            'backtrack_probability': 0.5,
            'walks_per_node': 10,
            'dynamic_window': True,
            'epochs_count': 1
        }

    def __call__(self):
        edges = self.data.get_link_edges_between_highest_ranked_nodes(
            self.config['node_count'])
        model = Embeddings(
            method=self.config['method'],
            dimensions=self.config['dimensions'],
            context_size=self.config['context_size'],
            backtrack_probability=self.config['backtrack_probability'],
            walks_per_node=self.config['walks_per_node'],
            epochs_count=self.config['epochs_count']
        )
        embeddings = model.train(data=edges)

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
            'point_count': 100000
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
            'neighbors_count': 10
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
            'neighbors_count': 10
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
            'depth': 1
        }

    def __call__(self):
        ids_category_names = self.data.get_ids_category_names_of_tsne_points()
        edges = self.data.get_edges_between_categories()
        categories = Graph.aggregate(
            ids_category_names,
            edges,
            depth=self.config['depth'])
        self.data.set_wikimap_categories(categories)


class CreateZoomIndex(Job):
    def __init__(self):
        super(CreateZoomIndex, self).__init__(
            'CREATE ZOOM INDEX',
            alias='zoom',
            inputs=[P.wikimap_points, P.pagerank],
            outputs=[P.zoom_index, P.wikimap_points, P.metadata])

        self.config = {
            'bucket_size': 100
        }

    def __call__(self):
        coords, ids = self.data.get_coords_ids_of_points()
        indexer = ZoomIndexer.Indexer(coords, ids, self.config['bucket_size'])
        self.data.set_zoom_index(indexer)
