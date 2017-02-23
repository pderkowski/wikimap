from Job import Job
from Paths import *
import Paths
import Interface
import Utils

class Build(object):
    def __init__(self):
        pages_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
        links_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'
        category_links_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz'
        page_properties_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page_props.sql.gz'
        redirects_url = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-redirect.sql.gz'

        jobs = []
        jobs.append(Job('DOWNLOAD PAGE TABLE', Utils.download(pages_url), inputs=[], outputs=[pages_dump]))
        jobs.append(Job('DOWNLOAD LINKS TABLE', Utils.download(links_url), inputs=[], outputs=[links_dump]))
        jobs.append(Job('DOWNLOAD CATEGORY LINKS TABLE', Utils.download(category_links_url), inputs=[], outputs=[category_links_dump]))
        jobs.append(Job('DOWNLOAD PAGE PROPERTIES TABLE', Utils.download(page_properties_url), inputs=[], outputs=[page_properties_dump]))
        jobs.append(Job('DOWNLOAD REDIRECTS TABLE', Utils.download(redirects_url), inputs=[], outputs=[redirects_dump]))
        jobs.append(Job('IMPORT PAGE TABLE', Interface.import_pages, inputs=[pages_dump], outputs=[pages]))
        jobs.append(Job('IMPORT LINKS TABLE', Interface.import_links, inputs=[links_dump], outputs=[links]))
        jobs.append(Job('IMPORT PAGE PROPERTIES TABLE', Interface.import_page_properties, inputs=[page_properties_dump], outputs=[page_properties]))
        jobs.append(Job('IMPORT CATEGORY LINKS TABLE', Interface.import_category_links, inputs=[category_links_dump, pages, page_properties], outputs=[category_links]))
        jobs.append(Job('IMPORT REDIRECTS TABLE', Interface.import_redirects, inputs=[redirects_dump], outputs=[redirects]))
        jobs.append(Job('CREATE LINK EDGES TABLE', Interface.create_link_edges, inputs=[links, pages], outputs=[link_edges]))
        jobs.append(Job('COMPUTE PAGERANK', Interface.compute_pagerank, inputs=[link_edges], outputs=[pagerank]))
        jobs.append(Job('CREATE ARTICLE MAPPING', Interface.create_article_mapping, inputs=[link_edges, pages, category_links, pagerank, redirects], outputs=[article_mapping]))
        jobs.append(Job('COMPUTE EMBEDDINGS WITH NODE2VEC', Interface.compute_embeddings_with_node2vec, inputs=[link_edges, pagerank], outputs=[embeddings], wordCount=1000000))
        jobs.append(Job('CREATE TITLE INDEX', Interface.create_title_index, inputs=[embeddings, pages, article_mapping], outputs=[title_index]))
        jobs.append(Job('EVALUATE EMBEDDINGS', Interface.evaluate_embeddings, inputs=[embeddings, title_index], outputs=[embedding_report]))
        jobs.append(Job('COMPUTE TSNE', Interface.compute_tsne, inputs=[embeddings, pagerank], outputs=[tsne], pointCount=100000))
        jobs.append(Job('COMPUTE HIGH DIMENSIONAL NEIGHBORS', Interface.compute_high_dimensional_neighbors, inputs=[embeddings, tsne, pages], outputs=[high_dimensional_neighbors]))
        jobs.append(Job('COMPUTE LOW DIMENSIONAL NEIGHBORS', Interface.compute_low_dimensional_neighbors, inputs=[tsne, pages], outputs=[low_dimensional_neighbors]))
        jobs.append(Job('CREATE AGGREGATED LINKS TABLES', Interface.create_aggregated_links, inputs=[link_edges, tsne], outputs=[aggregated_inlinks, aggregated_outlinks]))
        jobs.append(Job('CREATE WIKIMAP DATAPOINTS TABLE', Interface.create_wikimap_points, inputs=[tsne, pages, high_dimensional_neighbors, low_dimensional_neighbors, pagerank], outputs=[wikimap_points]))
        jobs.append(Job('CREATE WIKIMAP CATEGORIES TABLE', Interface.create_wikimap_categories, inputs=[category_links, pages, tsne], outputs=[wikimap_categories], depth=1))
        jobs.append(Job('CREATE ZOOM INDEX', Interface.create_zoom_index, inputs=[wikimap_points, pagerank], outputs=[zoom_index, metadata], bucketSize=100))
        jobs.append(Job('CREATE TERM INDEX', Interface.create_term_index, inputs=[wikimap_points, wikimap_categories], outputs=[term_index]))

        self.jobs = jobs

    def __iter__(self):
        return iter(self.jobs)

    def __getitem__(self, n):
        return self.jobs[n]

    def set_build_dir(self, path):
        Paths.global_base = path
