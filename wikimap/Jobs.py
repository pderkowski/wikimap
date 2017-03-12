from Builder.Job import Job
from Node2Vec import Node2Vec
import Pagerank
import TSNE
import NearestNeighbors
import ZoomIndexer
import Graph
import Data
import Paths as P

class DownloadPagesDump(Job):
    def __init__(self, url):
        super(DownloadPagesDump, self).__init__('DOWNLOAD PAGES DUMP',
            inputs=[], outputs=[P.pages_dump],
            url=url)

    def __call__(self, url):
        Data.download_pages_dump(url)

class DownloadLinksDump(Job):
    def __init__(self, url):
        super(DownloadLinksDump, self).__init__('DOWNLOAD LINKS DUMP',
            inputs=[], outputs=[P.links_dump],
            url=url)

    def __call__(self, url):
        Data.download_links_dump(url)

class DownloadCategoryLinksDump(Job):
    def __init__(self, url):
        super(DownloadCategoryLinksDump, self).__init__('DOWNLOAD CATEGORY LINKS DUMP',
            inputs=[], outputs=[P.category_links_dump],
            url=url)

    def __call__(self, url):
        Data.download_category_links_dump(url)

class DownloadPagePropertiesDump(Job):
    def __init__(self, url):
        super(DownloadPagePropertiesDump, self).__init__('DOWNLOAD PAGE PROPERTIES DUMP',
            inputs=[], outputs=[P.page_properties_dump],
            url=url)

    def __call__(self, url):
        Data.download_page_properties_dump(url)

class DownloadRedirectsDump(Job):
    def __init__(self, url):
        super(DownloadRedirectsDump, self).__init__('DOWNLOAD REDIRECTS DUMP',
            inputs=[], outputs=[P.redirects_dump],
            url=url)

    def __call__(self, url):
        Data.download_redirects_dump(url)

class DownloadEvaluationDatasets(Job):
    def __init__(self, url):
        super(DownloadEvaluationDatasets, self).__init__('DOWNLOAD EVALUATION DATASETS',
            inputs=[], outputs=[P.evaluation_files],
            url=url)

    def __call__(self, url):
        Data.download_evaluation_datasets(url)

class ImportPageTable(Job):
    def __init__(self):
        super(ImportPageTable, self).__init__('IMPORT PAGE TABLE', tag='pages',
            inputs=[P.pages_dump], outputs=[P.pages])

    def __call__(self):
        pages = Data.import_pages()
        Data.set_pages(pages)

class ImportLinksTable(Job):
    def __init__(self):
        super(ImportLinksTable, self).__init__('IMPORT LINKS TABLE', tag='links',
            inputs=[P.links_dump], outputs=[P.links])

    def __call__(self):
        links = Data.import_links()
        Data.set_links(links)

class ImportPagePropertiesTable(Job):
    def __init__(self):
        super(ImportPagePropertiesTable, self).__init__('IMPORT PAGE PROPERTIES TABLE', tag='props',
            inputs=[P.page_properties_dump], outputs=[P.page_properties])

    def __call__(self):
        page_properties = Data.import_page_properties()
        Data.set_page_properties(page_properties)

class ImportCategoryLinksTable(Job):
    def __init__(self):
        super(ImportCategoryLinksTable, self).__init__('IMPORT CATEGORY LINKS TABLE', tag='clinks',
            inputs=[P.category_links_dump, P.pages, P.page_properties], outputs=[P.category_links])

    def __call__(self):
        hidden_categories = Data.get_hidden_categories()
        category_links = Data.import_category_links()
        Data.set_category_links(category_links, hidden_categories)

class ImportRedirectsTable(Job):
    def __init__(self):
        super(ImportRedirectsTable, self).__init__('IMPORT REDIRECTS TABLE', tag='reds',
            inputs=[P.redirects_dump], outputs=[P.redirects])

    def __call__(self):
        redirects = Data.import_redirects()
        Data.set_redirects(redirects)

class CreateLinkEdgesTable(Job):
    def __init__(self):
        super(CreateLinkEdgesTable, self).__init__('CREATE LINK EDGES TABLE', tag='edges',
            inputs=[P.links, P.pages], outputs=[P.link_edges])

    def __call__(self):
        link_edges = Data.get_link_edges()
        Data.set_link_edges(link_edges)

class ComputePagerank(Job):
    def __init__(self):
        super(ComputePagerank, self).__init__('COMPUTE PAGERANK', tag='prank',
            inputs=[P.link_edges], outputs=[P.pagerank])

    def __call__(self):
        edges = Data.get_link_edges_as_strings()
        pagerank = Pagerank.pagerank(edges, stringified=True)
        Data.set_pagerank(pagerank)

class ComputeEmbeddings(Job):
    def __init__(self, node_count):
        super(ComputeEmbeddings, self).__init__('COMPUTE EMBEDDINGS', tag='embed',
            inputs=[P.link_edges, P.pagerank], outputs=[P.embeddings],
            node_count=node_count)

    def __call__(self, node_count):
        edges = Data.get_link_edges_between_highest_ranked_nodes(node_count)
        embeddings = Node2Vec(edges)
        Data.set_embeddings(embeddings)

class CreateTitleIndex(Job):
    def __init__(self):
        super(CreateTitleIndex, self).__init__('CREATE TITLE INDEX', tag='titles',
            inputs=[P.pages, P.category_links, P.redirects, P.embeddings], outputs=[P.title_index])

    def __call__(self):
        titles, ids = Data.get_titles_ids_including_redirects_excluding_disambiguations()
        Data.set_title_index(titles, ids)

class EvaluateEmbeddings(Job):
    def __init__(self, use_word_mapping):
        super(EvaluateEmbeddings, self).__init__('EVALUATE EMBEDDINGS', tag='eval',
            inputs=[P.evaluation_files, P.embeddings, P.title_index], outputs=[P.evaluation_report],
            use_word_mapping=use_word_mapping)

    def __call__(self, use_word_mapping):
        indexed_embeddings = Data.get_indexed_embeddings()
        evaluation_results = []
        word_mapping = Data.get_word_mapping() if use_word_mapping else {}
        for dataset in Data.get_evaluation_datasets(word_mapping=word_mapping):
            score, matched_examples, skipped_examples = dataset.evaluate(indexed_embeddings)
            evaluation_results.append((dataset.name, score, matched_examples, skipped_examples))
        Data.set_evaluation_results(evaluation_results)

class ComputeTSNE(Job):
    def __init__(self, point_count):
        super(ComputeTSNE, self).__init__('COMPUTE TSNE', tag='tsne',
            inputs=[P.embeddings, P.pagerank], outputs=[P.tsne],
            point_count=point_count)

    def __call__(self, point_count):
        ids, embeddings = Data.get_ids_embeddings_of_highest_ranked_points(point_count)
        mappings = TSNE.train(embeddings)
        Data.set_tsne_points(ids, mappings)

class ComputeHighDimensionalNeighbors(Job):
    def __init__(self, neighbors_count):
        super(ComputeHighDimensionalNeighbors, self).__init__('COMPUTE HIGH DIMENSIONAL NEIGHBORS', tag='hdnn',
            inputs=[P.embeddings, P.tsne, P.pages], outputs=[P.high_dimensional_neighbors],
            neighbors_count=neighbors_count)

    def __call__(self, neighbors_count):
        ids, titles, embeddings = Data.get_ids_titles_embeddings_of_tsne_points()
        distances, indices = NearestNeighbors.computeNearestNeighbors(embeddings, neighbors_count)
        Data.set_high_dimensional_neighbors(ids, titles, indices, distances)

class ComputeLowDimensionalNeighbors(Job):
    def __init__(self, neighbors_count):
        super(ComputeLowDimensionalNeighbors, self).__init__('COMPUTE LOW DIMENSIONAL NEIGHBORS', tag='ldnn',
            inputs=[P.tsne, P.pages], outputs=[P.low_dimensional_neighbors],
            neighbors_count=neighbors_count)

    def __call__(self, neighbors_count):
        ids, titles, tsne_points = Data.get_ids_titles_tsne_points()
        distances, indices = NearestNeighbors.computeNearestNeighbors(tsne_points, neighbors_count)
        Data.set_low_dimensional_neighbors(ids, titles, indices, distances)

class CreateAggregatedLinksTables(Job):
    def __init__(self):
        super(CreateAggregatedLinksTables, self).__init__('CREATE AGGREGATED LINKS TABLES', tag='agg',
            inputs=[P.link_edges, P.tsne], outputs=[P.aggregated_inlinks, P.aggregated_outlinks])

    def __call__(self):
        ids = list(Data.get_ids_of_tsne_points())
        outlinks = Data.get_outlinks_of_points(ids)
        inlinks = Data.get_inlinks_of_points(ids)
        Data.set_outlinks(outlinks)
        Data.set_inlinks(inlinks)

class CreateWikimapDatapointsTable(Job):
    def __init__(self):
        super(CreateWikimapDatapointsTable, self).__init__('CREATE WIKIMAP DATAPOINTS TABLE', tag='points',
            inputs=[P.tsne, P.pages, P.high_dimensional_neighbors, P.low_dimensional_neighbors, P.pagerank], outputs=[P.wikimap_points])

    def __call__(self):
        points = Data.get_wikimap_points()
        Data.set_wikimap_points(points)

class CreateWikimapCategoriesTable(Job):
    def __init__(self, depth):
        super(CreateWikimapCategoriesTable, self).__init__('CREATE WIKIMAP CATEGORIES TABLE', tag='cats',
            inputs=[P.category_links, P.pages, P.tsne], outputs=[P.wikimap_categories],
            depth=depth)

    def __call__(self, depth):
        ids_category_names = Data.get_ids_category_names_of_tsne_points()
        edges = Data.get_edges_between_categories()
        categories = Graph.aggregate(ids_category_names, edges, depth=depth)
        Data.set_wikimap_categories(categories)

class CreateZoomIndex(Job):
    def __init__(self, bucket_size):
        super(CreateZoomIndex, self).__init__('CREATE ZOOM INDEX', tag='zoom',
            inputs=[P.wikimap_points, P.pagerank], outputs=[P.zoom_index, P.wikimap_points, P.metadata],
            bucket_size=bucket_size)

    def __call__(self, bucket_size):
        coords, ids = Data.get_coords_ids_of_points()
        indexer = ZoomIndexer.Indexer(coords, ids, bucket_size)
        Data.set_zoom_index(indexer)
