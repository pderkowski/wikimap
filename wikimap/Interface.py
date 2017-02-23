from Node2Vec import Node2Vec
import Tables
import Pagerank
import TSNE
import NearestNeighbors
import ZoomIndexer
import Graph
import Evaluation
import Data

def import_pages(pages_dump_path, output_path):
    pages = Data.import_pages(pages_dump_path)
    Data.set_pages(pages, output_path)

def import_links(links_dump_path, output_path):
    links = Data.import_links(links_dump_path)
    Data.set_links(links, output_path)

def import_page_properties(page_properties_dump_path, output_path):
    page_properties = Data.import_page_properties(page_properties_dump_path)
    Data.set_page_properties(page_properties, output_path)

def import_category_links(category_links_dump_path, pages_path, page_properties_path, output_path):
    hidden_categories = Data.get_hidden_categories(pages_path, page_properties_path)
    category_links = Data.import_category_links(category_links_dump_path)
    Data.set_category_links(hidden_categories, category_links, output_path)

def import_redirects(redirects_dump_path, output_path):
    redirects = Data.import_redirects(redirects_dump_path)
    Data.set_redirects(redirects, output_path)

def create_link_edges(links_path, pages_path, output_path):
    link_edges = Data.get_link_edges(links_path, pages_path)
    Data.set_edges(link_edges, output_path)

def create_wikimap_points(tsne_path, pages_path, hdn_path, ldn_path, pagerank_path, output_path):
    points = Data.get_wikimap_points(tsne_path, pages_path, hdn_path, ldn_path, pagerank_path)
    Data.set_wikimap_points(points, output_path)

def create_aggregated_links(edges_path, tsne_path, inlink_path, outlink_path):
    ids = Data.get_ids_of_tsne_points(tsne_path)
    outlinks = Data.get_outlinks_of_points(edges_path, ids)
    inlinks = Data.get_inlinks_of_points(edges_path, ids)
    Data.set_outlinks(outlinks, outlink_path)
    Data.set_inlinks(inlinks, inlink_path)

def compute_pagerank(edges_path, output_path):
    edges = Data.get_edges_as_strings(edges_path)
    pagerank = Pagerank.pagerank(edges, stringified=True)
    Data.set_pagerank(pagerank, output_path)

def compute_embeddings_with_node2vec(edges_path, pagerank_path, output_path, node_count=1000000):
    edges = Data.get_edges_between_highest_ranked_nodes(edges_path, pagerank_path, node_count=node_count)
    embeddings = Node2Vec(edges)
    Data.set_embeddings(embeddings, output_path)

def compute_tsne(embeddings_path, pagerank_path, output_path, point_count=100000):
    ids, embeddings = Data.get_ids_embeddings_of_highest_ranked_points(embeddings_path, pagerank_path, point_count=point_count)
    mappings = TSNE.train(embeddings)
    Data.set_tsne_points(ids, mappings, output_path)

def compute_high_dimensional_neighbors(embeddings_path, tsne_path, pages_path, output_path, neighbors_count=10):
    ids, titles, embeddings = Data.get_ids_titles_embeddings_of_tsne_points(embeddings_path, tsne_path, pages_path)
    distances, indices = NearestNeighbors.computeNearestNeighbors(embeddings, neighbors_count)
    Data.set_high_dimensional_neighbors(ids, titles, indices, distances, output_path)

def compute_low_dimensional_neighbors(tsne_path, pages_path, output_path, neighbors_count=10):
    ids, titles, tsne_points = Data.get_ids_titles_tsne_points(tsne_path, pages_path)
    distances, indices = NearestNeighbors.computeNearestNeighbors(tsne_points, neighbors_count)
    Data.set_low_dimensional_neighbors(ids, titles, indices, distances, output_path)

def create_wikimap_categories(category_links_path, pages_path, tsne_path, output_path, depth=1):
    ids_category_names = Data.get_ids_category_names_of_tsne_points(category_links_path, tsne_path)
    edges = Data.get_edges_between_categories(category_links_path, pages_path)
    categories = Graph.aggregate(ids_category_names, edges, depth=depth)
    Data.set_categories(categories, output_path)

def create_zoom_index(wikipoints_path, pagerank_path, zoom_index_path, metadata_path, bucket_size=100):
    coords, ids = Data.get_coords_ids_of_points(wikipoints_path, pagerank_path)
    indexer = ZoomIndexer.Indexer(coords, ids, bucket_size)
    Data.set_zoom_index(indexer, zoom_index_path, wikipoints_path, metadata_path)

def create_term_index(wikipoints_path, wikicategories_path, output_path):
    point_titles, category_titles = Data.get_terms(wikipoints_path, wikicategories_path)
    Data.set_term_index(point_titles, category_titles, output_path)

def create_article_mapping(link_edges_path, pages_path, category_links_path, pagerank_path, redirects_path, output_path):
    article_ids = Data.get_article_ids(pages_path)
    disambiguations = Data.get_disambiguations(link_edges_path, pages_path, category_links_path, pagerank_path)
    redirects = Data.get_redirects(redirects_path, pages_path)
    Data.set_article_mapping(article_ids, disambiguations, redirects, output_path)

def create_title_index(embeddings_path, pages_path, article_mapping_path, output_path):
    article_mapping = Data.get_article_mapping(article_mapping_path)
    ids, titles = Data.get_ids_titles_of_embeddings(embeddings_path, pages_path)
    Data.set_title_index(ids, titles, article_mapping, output_path)

def evaluate_embeddings(embeddings_path, title_index, outputPath):
    indexed_embeddings_table = Tables.IndexedEmbeddingsTable(embeddings_path, title_index)
    Evaluation.check(indexed_embeddings_table)
