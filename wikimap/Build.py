from Job import Job
from Paths import *
import Paths
import Interface

class Build(object):
    def __init__(self):
        pages_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
        links_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'
        category_links_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz'
        page_properties_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page_props.sql.gz'
        redirects_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-redirect.sql.gz'
        evaluation_datasets_url = 'https://dl.dropboxusercontent.com/u/71728465/datasets.tar.gz'

        jobs = []
        jobs.append(Job('DOWNLOAD PAGE TABLE', Interface.download_pages_dump, inputs=[], outputs=[pages_dump],
            url=pages_url))
        jobs.append(Job('DOWNLOAD LINKS TABLE', Interface.download_links_dump, inputs=[], outputs=[links_dump],
            url=links_url))
        jobs.append(Job('DOWNLOAD CATEGORY LINKS TABLE', Interface.download_category_links_dump, inputs=[], outputs=[category_links_dump],
            url=category_links_url))
        jobs.append(Job('DOWNLOAD PAGE PROPERTIES TABLE', Interface.download_page_properties_dump, inputs=[], outputs=[page_properties_dump],
            url=page_properties_url))
        jobs.append(Job('DOWNLOAD REDIRECTS TABLE', Interface.download_redirects_dump, inputs=[], outputs=[redirects_dump],
            url=redirects_url))
        jobs.append(Job('DOWNLOAD EVALUATION DATASETS', Interface.download_evaluation_datasets, inputs=[], outputs=[evaluation_files],
            url=evaluation_datasets_url))
        jobs.append(Job('IMPORT PAGE TABLE', Interface.import_pages, inputs=[pages_dump], outputs=[pages]))
        jobs.append(Job('IMPORT LINKS TABLE', Interface.import_links, inputs=[links_dump], outputs=[links]))
        jobs.append(Job('IMPORT PAGE PROPERTIES TABLE', Interface.import_page_properties, inputs=[page_properties_dump], outputs=[page_properties]))
        jobs.append(Job('IMPORT CATEGORY LINKS TABLE', Interface.import_category_links, inputs=[category_links_dump, pages, page_properties], outputs=[category_links]))
        jobs.append(Job('IMPORT REDIRECTS TABLE', Interface.import_redirects, inputs=[redirects_dump], outputs=[redirects]))
        jobs.append(Job('CREATE LINK EDGES TABLE', Interface.create_link_edges, inputs=[links, pages], outputs=[link_edges]))
        jobs.append(Job('COMPUTE PAGERANK', Interface.compute_pagerank, inputs=[link_edges], outputs=[pagerank]))
        jobs.append(Job('COMPUTE EMBEDDINGS WITH NODE2VEC', Interface.compute_embeddings_with_node2vec, inputs=[link_edges, pagerank], outputs=[embeddings],
            node_count=1000000))
        jobs.append(Job('CREATE TITLE INDEX', Interface.create_title_index, inputs=[link_edges, pages, category_links, pagerank, redirects, embeddings], outputs=[title_index]))
        jobs.append(Job('EVALUATE EMBEDDINGS', Interface.evaluate_embeddings, inputs=[evaluation_files, embeddings, title_index], outputs=[evaluation_report],
            use_word_mapping=False))
        jobs.append(Job('COMPUTE TSNE', Interface.compute_tsne, inputs=[embeddings, pagerank], outputs=[tsne],
            point_count=100000))
        jobs.append(Job('COMPUTE HIGH DIMENSIONAL NEIGHBORS', Interface.compute_high_dimensional_neighbors, inputs=[embeddings, tsne, pages], outputs=[high_dimensional_neighbors],
            neighbors_count=10))
        jobs.append(Job('COMPUTE LOW DIMENSIONAL NEIGHBORS', Interface.compute_low_dimensional_neighbors, inputs=[tsne, pages], outputs=[low_dimensional_neighbors],
            neighbors_count=10))
        jobs.append(Job('CREATE AGGREGATED LINKS TABLES', Interface.create_aggregated_links, inputs=[link_edges, tsne], outputs=[aggregated_inlinks, aggregated_outlinks]))
        jobs.append(Job('CREATE WIKIMAP DATAPOINTS TABLE', Interface.create_wikimap_points, inputs=[tsne, pages, high_dimensional_neighbors, low_dimensional_neighbors, pagerank], outputs=[wikimap_points]))
        jobs.append(Job('CREATE WIKIMAP CATEGORIES TABLE', Interface.create_wikimap_categories, inputs=[category_links, pages, tsne], outputs=[wikimap_categories],
            depth=0))
        jobs.append(Job('CREATE ZOOM INDEX', Interface.create_zoom_index, inputs=[wikimap_points, pagerank], outputs=[zoom_index, wikimap_points, metadata],
            bucket_size=100))

        self.jobs = jobs

    def __iter__(self):
        return iter(self.jobs)

    def __getitem__(self, n):
        return self.jobs[n]

    def set_build_dir(self, path):
        Paths.global_base = path
