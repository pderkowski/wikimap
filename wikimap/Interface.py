from common.Zoom import ZoomIndex
from common.Terms import TermIndex
from Node2Vec import Node2Vec
from Utils import LogIt, GroupIt, ColumnIt, FlipIt, pipe, NotEqualIt, NotInIt
import Tables
import Pagerank
import TSNE
import NearestNeighbors
import ZoomIndexer
import Graph
import shelve
from itertools import imap, izip, repeat
from operator import itemgetter

def createPageTable(pagePath, outputPath):
    source = Tables.Import.PageTable(pagePath)
    table = Tables.PageTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createLinksTable(linksPath, outputPath):
    source = Tables.Import.LinksTable(linksPath)
    table = Tables.LinksTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createPagePropertiesTable(pagePropertiesPath, outputPath):
    source = Tables.Import.PagePropertiesTable(pagePropertiesPath)
    table = Tables.PagePropertiesTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createCategoryLinksTable(categoryLinksPath, pageTablePath, pagePropertiesTablePath, outputPath):
    joined = Tables.Join(pageTablePath, pagePropertiesTablePath)
    hiddenCategories = frozenset(ColumnIt(0)(joined.selectHiddenCategories()))

    table = Tables.CategoryLinksTable(outputPath)
    table.create()

    source = Tables.Import.CategoryLinksTable(categoryLinksPath)
    table.populate(pipe(source.read(), NotInIt(hiddenCategories, 1), LogIt(1000000)))

def createEdgeArray(pagesPath, linksPath, outputPath):
    joined = Tables.Join(pagesPath, linksPath)
    edges = Tables.EdgeTable(outputPath)
    edges.populate(LogIt(1000000)(joined.selectNormalizedLinks()))

def createWikimapPointsTable(tsnePath, pagePath, hdnnPath, ldnnPath, pagerankPath, outputPath):
    data = Tables.Join(tsnePath, pagePath, hdnnPath, ldnnPath, pagerankPath)

    table = Tables.WikimapPointsTable(outputPath)
    table.create()

    table.populate(data.selectWikimapPoints())

def createAggregatedLinksTables(edgeArrayPath, tsnePath, inlinkTablePath, outlinkTablePath):
    tsne = Tables.TSNETable(tsnePath)
    ids = ColumnIt(0)(tsne.selectAll())

    edges = Tables.EdgeTable(edgeArrayPath)
    edges.filterByNodes(ids)

    outlinks = Tables.AggregatedLinksTable(outlinkTablePath)
    edges.sortByStartNode()
    outlinks.create(pipe(edges, LogIt(1000000), GroupIt))

    inlinks = Tables.AggregatedLinksTable(inlinkTablePath)
    edges.inverseEdges()
    edges.sortByStartNode()
    inlinks.create(pipe(edges, LogIt(1000000), GroupIt))

def computePagerank(edgeArrayPath, pagerankPath):
    edges = Tables.EdgeTable(edgeArrayPath, stringify=True)
    pagerank = Tables.PagerankTable(pagerankPath)
    pagerank.create()
    pagerank.populate(Pagerank.pagerank(edges, stringified=True))

def computeEmbeddingsWithNode2Vec(edgeArrayPath, pagerankPath, outputPath, wordCount=1000000):
    edges = Tables.EdgeTable(edgeArrayPath)
    pagerank = Tables.PagerankTable(pagerankPath)
    ids = list(ColumnIt(0)(pagerank.selectIdsByDescendingRank(wordCount)))
    edges.filterByNodes(ids)
    embeddingsTable = Tables.EmbeddingsTable(outputPath)
    edges = LogIt(1000000, start="Reading edges...")(edges)
    embeddings = LogIt(100000)(Node2Vec(edges))
    embeddingsTable.create(embeddings)

def computeTSNE(embeddingsPath, pagerankPath, tsnePath, pointCount=10000):
    pagerank = Tables.PagerankTable(pagerankPath)

    ids = pipe(pagerank.selectIdsByDescendingRank(pointCount), ColumnIt(0), list)
    embeddings = Tables.EmbeddingsTable(embeddingsPath)
    mappings = TSNE.train(embeddings.get(id_) for id_ in ids)

    tsne = Tables.TSNETable(tsnePath)
    tsne.create()
    tsne.populate(izip(ids, mappings[:, 0], mappings[:, 1]))

def computeHighDimensionalNeighbors(embeddingsPath, tsnePath, pagePath, outputPath, neighborsNo=10):
    joined = Tables.Join(tsnePath, pagePath)

    data = list(joined.select_id_title_tsneX_tsneY())
    ids, titles = list(ColumnIt(0)(data)), list(ColumnIt(1)(data))
    embeddingsTable = Tables.EmbeddingsTable(embeddingsPath)
    embeddings = imap(embeddingsTable.get, ids)
    distances, indices = NearestNeighbors.computeNearestNeighbors(embeddings, neighborsNo)

    table = Tables.HighDimensionalNeighborsTable(outputPath)
    table.create()
    table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

def computeLowDimensionalNeighbors(tsnePath, pagePath, outputPath, neighborsNo=10):
    joined = Tables.Join(tsnePath, pagePath)

    data = list(joined.select_id_title_tsneX_tsneY())
    ids, titles, points = list(ColumnIt(0)(data)), list(ColumnIt(1)(data)), ColumnIt(2, 3)(data)

    table = Tables.LowDimensionalNeighborsTable(outputPath)
    table.create()

    distances, indices = NearestNeighbors.computeNearestNeighbors(points, neighborsNo)
    table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

def createWikimapCategoriesTable(categoryLinksPath, pagesPath, tsnePath, outputPath, depth=1):
    data = Tables.Join(categoryLinksPath, pagesPath, tsnePath)

    table = Tables.WikimapCategoriesTable(outputPath)
    table.create()

    table.populate(pipe(Graph.aggregate(data.select_id_category(), data.selectCategoryLinks(), depth=depth), NotEqualIt([], 1), LogIt(100000)))

def createZoomIndex(wikipointsPath, pagerankPath, indexPath, metadataPath, bucketSize=100):
    joined = Tables.Join(wikipointsPath, pagerankPath)

    data = list(joined.select_id_x_y_byRank())
    indexer = ZoomIndexer.Indexer(ColumnIt(1, 2)(data), ColumnIt(0)(data), bucketSize)

    zoom = ZoomIndex(indexPath)
    zoom.build(indexer.index2data())

    wikipoints = Tables.WikimapPointsTable(wikipointsPath)
    wikipoints.updateIndex(FlipIt(indexer.data2index()))

    metadata = shelve.open(metadataPath)
    metadata['bounds'] = indexer.getBounds()
    metadata.close()

def createTermIndex(wikipointsPath, wikicategoriesPath, outputPath):
    wikipoints = Tables.WikimapPointsTable(wikipointsPath)
    categories = Tables.WikimapCategoriesTable(wikicategoriesPath)

    termIndex = TermIndex(outputPath)
    termIndex.add(izip(imap(itemgetter(0), wikipoints.selectTitles()), repeat(False)))
    termIndex.add(izip(imap(itemgetter(0), categories.selectTitles()), repeat(True)))

def createEmbeddingIndex(embeddingsPath, pagePath, outputPath):
    embeddingsTable = Tables.EmbeddingsTable(embeddingsPath)
    pageTable = Tables.PageTable(pagePath)

    ids = embeddingsTable.keys()
    data = pipe(pageTable.select_id_title(ids), FlipIt)

    index = Tables.EmbeddingIndex(outputPath)
    index.create(data)

# def evaluateEmbeddings(embeddingsPath, outputPath):
#     embeddingsTable = Tables.EmbeddingsTable(embeddingsPath)
