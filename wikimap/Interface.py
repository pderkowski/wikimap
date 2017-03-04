from Node2Vec import Node2Vec
import Pagerank
import TSNE
import NearestNeighbors
import ZoomIndexer
import Graph
import Data

def download_pages_dump(url):
    Data.download_pages_dump(url)

def download_links_dump(url):
    Data.download_links_dump(url)

def download_category_links_dump(url):
    Data.download_category_links_dump(url)

def download_page_properties_dump(url):
    Data.download_page_properties_dump(url)

def download_redirects_dump(url):
    Data.download_redirects_dump(url)

def download_evaluation_datasets(url):
    Data.download_evaluation_datasets(url)

def import_pages():
    pages = Data.import_pages()
    Data.set_pages(pages)

def import_links():
    links = Data.import_links()
    Data.set_links(links)

def import_page_properties():
    page_properties = Data.import_page_properties()
    Data.set_page_properties(page_properties)

def import_category_links():
    hidden_categories = Data.get_hidden_categories()
    category_links = Data.import_category_links()
    Data.set_category_links(category_links, hidden_categories)

def import_redirects():
    redirects = Data.import_redirects()
    Data.set_redirects(redirects)

def create_link_edges():
    link_edges = Data.get_link_edges()
    Data.set_link_edges(link_edges)

def compute_pagerank():
    edges = Data.get_link_edges_as_strings()
    pagerank = Pagerank.pagerank(edges, stringified=True)
    Data.set_pagerank(pagerank)

def compute_embeddings_with_node2vec(node_count):
    edges = Data.get_link_edges_between_highest_ranked_nodes(node_count)
    embeddings = Node2Vec(edges)
    Data.set_embeddings(embeddings)

def create_title_index():
    titles, ids = Data.get_titles_ids_including_redirects_excluding_disambiguations()
    Data.set_title_index(titles, ids)

def evaluate_embeddings(use_word_mapping):
    indexed_embeddings = Data.get_indexed_embeddings()
    evaluation_results = []
    word_mapping = Data.get_word_mapping() if use_word_mapping else {}
    for dataset in Data.get_evaluation_datasets(word_mapping=word_mapping):
        # dataset.check_vocabulary(indexed_embeddings, verbose=True)
        score, matched_examples, skipped_examples = dataset.evaluate(indexed_embeddings)
        evaluation_results.append((dataset.name, score, matched_examples, skipped_examples))
    Data.set_evaluation_results(evaluation_results)

def compute_tsne(point_count):
    ids, embeddings = Data.get_ids_embeddings_of_highest_ranked_points(point_count)
    mappings = TSNE.train(embeddings)
    Data.set_tsne_points(ids, mappings)

def compute_high_dimensional_neighbors(neighbors_count):
    ids, titles, embeddings = Data.get_ids_titles_embeddings_of_tsne_points()
    distances, indices = NearestNeighbors.computeNearestNeighbors(embeddings, neighbors_count)
    Data.set_high_dimensional_neighbors(ids, titles, indices, distances)

def compute_low_dimensional_neighbors(neighbors_count):
    ids, titles, tsne_points = Data.get_ids_titles_tsne_points()
    distances, indices = NearestNeighbors.computeNearestNeighbors(tsne_points, neighbors_count)
    Data.set_low_dimensional_neighbors(ids, titles, indices, distances)

def create_aggregated_links():
    ids = list(Data.get_ids_of_tsne_points())
    outlinks = Data.get_outlinks_of_points(ids)
    inlinks = Data.get_inlinks_of_points(ids)
    Data.set_outlinks(outlinks)
    Data.set_inlinks(inlinks)

def create_wikimap_points():
    points = Data.get_wikimap_points()
    Data.set_wikimap_points(points)

def create_wikimap_categories(depth):
    ids_category_names = Data.get_ids_category_names_of_tsne_points()
    edges = Data.get_edges_between_categories()
    categories = Graph.aggregate(ids_category_names, edges, depth=depth)
    Data.set_wikimap_categories(categories)

def create_zoom_index(bucket_size):
    coords, ids = Data.get_coords_ids_of_points()
    indexer = ZoomIndexer.Indexer(coords, ids, bucket_size)
    Data.set_zoom_index(indexer)
