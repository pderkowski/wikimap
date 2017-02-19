from common import SQLTableDefs
from common.Zoom import ZoomIndex
from common.Terms import TermIndex
from Node2Vec import Node2Vec
from Tables import EdgeArray
from Utils import LogIt, GroupIt, ColumnIt, FlipIt, pipe, NotInIt, NotEqualIt
import Tools
import Pagerank
import TSNE
import NearestNeighbors
import ZoomIndexer
import Graph
import shelve
from itertools import imap, izip, repeat
from operator import itemgetter

def createPageTable(pageSql, outputPath):
    source = Tools.TableImporter(pageSql, Tools.getPageRecords, "page")
    table = SQLTableDefs.PageTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createLinksTable(linksSql, outputPath):
    source = Tools.TableImporter(linksSql, Tools.getLinksRecords, "pagelinks")
    table = SQLTableDefs.LinksTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createPagePropertiesTable(pagePropertiesSql, outputPath):
    source = Tools.TableImporter(pagePropertiesSql, Tools.getPagePropertiesRecords, "page_props")
    table = SQLTableDefs.PagePropertiesTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createCategoryLinksTable(categoryLinksSql, pageTablePath, pagePropertiesTablePath, outputPath):
    joined = SQLTableDefs.Join(pageTablePath, pagePropertiesTablePath)
    hiddenCategories = frozenset(ColumnIt(0)(joined.selectHiddenCategories()))

    table = SQLTableDefs.CategoryLinksTable(outputPath)
    table.create()

    source = Tools.TableImporter(categoryLinksSql, Tools.getCategoryLinksRecords, "categorylinks")
    table.populate(pipe(source.read(), NotInIt(hiddenCategories, 1), LogIt(1000000)))

def createAggregatedLinksTables(edgeArrayPath, tsnePath, inlinkTablePath, outlinkTablePath):
    tsne = SQLTableDefs.TSNETable(tsnePath)
    ids = ColumnIt(0)(tsne.selectAll())

    edges = EdgeArray(edgeArrayPath)
    edges.filterByNodes(ids)

    outlinks = SQLTableDefs.AggregatedLinksTable(outlinkTablePath)
    edges.sortByStartNode()
    outlinks.create(pipe(edges, LogIt(1000000), GroupIt))

    inlinks = SQLTableDefs.AggregatedLinksTable(inlinkTablePath)
    edges.inverseEdges()
    edges.sortByStartNode()
    inlinks.create(pipe(edges, LogIt(1000000), GroupIt))

def computePagerank(edgeArrayPath, pagerankPath):
    edges = EdgeArray(edgeArrayPath, stringify=True)
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    pagerank.create()
    pagerank.populate(Pagerank.pagerank(edges, stringified=True))

def computeEmbeddingsWithNode2Vec(edgeArrayPath, pagerankPath, outputPath, wordCount=1000000):
    edges = EdgeArray(edgeArrayPath)
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    ids = list(ColumnIt(0)(pagerank.selectIdsByDescendingRank(wordCount)))
    edges.filterByNodes(ids)
    embeddingsTable = SQLTableDefs.EmbeddingsTable(outputPath)
    edges = LogIt(1000000, start="Reading edges...")(edges)
    embeddings = LogIt(100000)(Node2Vec(edges))
    embeddingsTable.create(embeddings)

def computeTSNE(embeddingsPath, pagerankPath, tsnePath, pointCount=10000):
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)

    ids = pipe(pagerank.selectIdsByDescendingRank(pointCount), ColumnIt(0), list)
    embeddings = SQLTableDefs.EmbeddingsTable(embeddingsPath)
    mappings = TSNE.train(embeddings.get(id_) for id_ in ids)

    tsne = SQLTableDefs.TSNETable(tsnePath)
    tsne.create()
    tsne.populate(izip(ids, mappings[:, 0], mappings[:, 1]))

def computeHighDimensionalNeighbors(embeddingsPath, tsnePath, pagePath, outputPath, neighborsNo=10):
    joined = SQLTableDefs.Join(tsnePath, pagePath)

    data = list(joined.select_id_title_tsneX_tsneY())
    ids, titles = list(ColumnIt(0)(data)), list(ColumnIt(1)(data))
    embeddingsTable = SQLTableDefs.EmbeddingsTable(embeddingsPath)
    embeddings = imap(embeddingsTable.get, ids)

    table = SQLTableDefs.HighDimensionalNeighborsTable(outputPath)
    table.create()

    distances, indices = NearestNeighbors.computeNearestNeighbors(embeddings, neighborsNo)
    table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

def computeLowDimensionalNeighbors(tsnePath, pagePath, outputPath, neighborsNo=10):
    joined = SQLTableDefs.Join(tsnePath, pagePath)

    data = list(joined.select_id_title_tsneX_tsneY())
    ids, titles, points = list(ColumnIt(0)(data)), list(ColumnIt(1)(data)), ColumnIt(2, 3)(data)

    table = SQLTableDefs.LowDimensionalNeighborsTable(outputPath)
    table.create()

    distances, indices = NearestNeighbors.computeNearestNeighbors(points, neighborsNo)
    table.populate(izip(ids, imap(lambda a: [titles[i] for i in a], indices), imap(list, distances)))

def createWikimapPointsTable(tsnePath, pagePath, hdnnPath, ldnnPath, pagerankPath, outputPath):
    data = SQLTableDefs.Join(tsnePath, pagePath, hdnnPath, ldnnPath, pagerankPath)

    table = SQLTableDefs.WikimapPointsTable(outputPath)
    table.create()

    table.populate(data.selectWikimapPoints())

def createWikimapCategoriesTable(categoryLinksPath, pagesPath, tsnePath, outputPath, depth=1):
    data = SQLTableDefs.Join(categoryLinksPath, pagesPath, tsnePath)

    table = SQLTableDefs.WikimapCategoriesTable(outputPath)
    table.create()

    table.populate(pipe(Graph.aggregate(data.select_id_category(), data.selectCategoryLinks(), depth=depth), NotEqualIt([], 1), LogIt(100000)))

def createZoomIndex(wikipointsPath, pagerankPath, indexPath, metadataPath, bucketSize=100):
    joined = SQLTableDefs.Join(wikipointsPath, pagerankPath)

    data = list(joined.select_id_x_y_byRank())
    indexer = ZoomIndexer.Indexer(ColumnIt(1, 2)(data), ColumnIt(0)(data), bucketSize)

    zoom = ZoomIndex(indexPath)
    zoom.build(indexer.index2data())

    wikipoints = SQLTableDefs.WikimapPointsTable(wikipointsPath)
    wikipoints.updateIndex(FlipIt(indexer.data2index()))

    metadata = shelve.open(metadataPath)
    metadata['bounds'] = indexer.getBounds()
    metadata.close()

def createTermIndex(wikipointsPath, wikicategoriesPath, outputPath):
    wikipoints = SQLTableDefs.WikimapPointsTable(wikipointsPath)
    categories = SQLTableDefs.WikimapCategoriesTable(wikicategoriesPath)

    termIndex = TermIndex(outputPath)
    termIndex.add(izip(imap(itemgetter(0), wikipoints.selectTitles()), repeat(False)))
    termIndex.add(izip(imap(itemgetter(0), categories.selectTitles()), repeat(True)))

# def evaluateEmbeddings(embeddingsPath, outputPath):
#     embeddingsTable = SQLTableDefs.EmbeddingsTable(embeddingsPath)
