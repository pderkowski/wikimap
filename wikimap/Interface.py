from common import SQLTableDefs
import Tools
import Pagerank
import Word2Vec
import TSNE
import NearestNeighbors
import Stats
import Plots
import ZoomIndexer
import shelve
from common.Zoom import ZoomIndex
from common.Terms import TermIndex
from itertools import imap, izip, repeat
from operator import itemgetter
from Utils import StringifyIt, LogIt, DeferIt, GroupIt, JoinIt, ColumnIt, UnconsIt, FlipIt, SumIt, pipe

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

def createCategoryTable(categorySql, outputPath):
    source = Tools.TableImporter(categorySql, Tools.getCategoryRecords, "category")
    table = SQLTableDefs.CategoryTable(outputPath)
    table.create()
    table.populate(source.read())

def createPagePropertiesTable(pagePropertiesSql, outputPath):
    source = Tools.TableImporter(pagePropertiesSql, Tools.getPagePropertiesRecords, "page_props")
    table = SQLTableDefs.PagePropertiesTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createCategoryLinksTable(categoryLinksSql, outputPath):
    source = Tools.TableImporter(categoryLinksSql, Tools.getCategoryLinksRecords, "categorylinks")
    table = SQLTableDefs.CategoryLinksTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createNormalizedLinksTable(pageTable, linksTable, outputPath):
    source = SQLTableDefs.Join(pageTable, linksTable)
    table = SQLTableDefs.NormalizedLinksTable(outputPath)
    table.create()
    table.populate(source.selectNormalizedLinks())

def computePagerank(normalizedLinksPath, pagerankPath):
    normLinks = SQLTableDefs.NormalizedLinksTable(normalizedLinksPath)
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    pagerank.create()
    pagerank.populate(Pagerank.pagerank(pipe(normLinks.selectAll())))

def computeVocabulary(normalizedLinksPath, outputPath):
    normLinks = SQLTableDefs.NormalizedLinksTable(normalizedLinksPath)
    Word2Vec.buildVocabulary(pipe(normLinks.selectAll, DeferIt, StringifyIt), outputPath)

def computeEmbeddings(normalizedLinksPath, vocabularyPath, outputPath):
    normLinks = SQLTableDefs.NormalizedLinksTable(normalizedLinksPath)
    Word2Vec.train(pipe(normLinks.selectAll, DeferIt, StringifyIt), vocabularyPath, outputPath)

def computeTSNE(embeddingsPath, pagerankPath, tsnePath, pointCount=10000):
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)

    ids = pipe(pagerank.selectIdsByDescendingRank(pointCount), StringifyIt, ColumnIt(0), list)
    mappings = TSNE.train(Word2Vec.getEmbeddings(embeddingsPath, ids))

    tsne = SQLTableDefs.TSNETable(tsnePath)
    tsne.create()
    tsne.populate(izip(ids, mappings[:, 0], mappings[:, 1]))

def computeHighDimensionalNeighbors(embeddingsPath, tsnePath, pagePath, outputPath, neighborsNo=10):
    joined = SQLTableDefs.Join(tsnePath, pagePath)

    data = list(joined.select_id_title_tsneX_tsneY())
    ids, titles = list(ColumnIt(0)(data)), list(ColumnIt(1)(data))
    embeddings = Word2Vec.getEmbeddings(embeddingsPath, imap(str, ids))

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

def createWikimapCategoriesTable(categoryLinksPath, categoryPath, pagesPath, tsnePath, pagePropertiesPath, outputPath):
    data = SQLTableDefs.Join(categoryLinksPath, pagesPath, tsnePath, categoryPath, pagePropertiesPath)

    table = SQLTableDefs.WikimapCategoriesTable(outputPath)
    table.create()

    table.populate(pipe(data.selectWikimapCategories(), GroupIt, UnconsIt))

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

def createDegreesTable(tsnePath, normalizedLinksPath, outputPath):
    tsne = SQLTableDefs.TSNETable(tsnePath)
    normLinks = SQLTableDefs.NormalizedLinksTable(normalizedLinksPath)

    ids = ColumnIt(0)(tsne.selectAll())
    links = normLinks.selectAll()

    degrees = SQLTableDefs.DegreesTable(outputPath)
    degrees.create()

    degrees.populate(Stats.countInOutDegrees(ids, links))

def createDegreePlot(degreesPath, degreePlotPath, maxDegree=30):
    degrees = SQLTableDefs.DegreesTable(degreesPath)
    plot = Plots.createDegreePlot(degrees.select_degree_count(maxDegree=maxDegree), maxDegree=maxDegree)
    plot.savefig(degreePlotPath)

def createIsolatedPointsPlot(degreesPath, pagerankPath, outputPath, degreeThreshold=30):
    degrees = SQLTableDefs.DegreesTable(degreesPath)

    isolatedIds = ColumnIt(0)(degrees.selectIdsByMaxDegree(degreeThreshold))

    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    isolatedOrders = ColumnIt(0)(pagerank.selectOrdersByIds(isolatedIds))

    plot = Plots.createPointOrdersPlot(isolatedOrders)
    plot.savefig(outputPath)
