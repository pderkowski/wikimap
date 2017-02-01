from common import SQLTableDefs
import Arrays
import Tools
import Pagerank
from Word2Vec import Word2Vec
from Node2Vec import Node2Vec
import TSNE
import NearestNeighbors
import ZoomIndexer
import shelve
import Graph
from common.Zoom import ZoomIndex
from common.Terms import TermIndex
from itertools import imap, izip, repeat
from operator import itemgetter
from Utils import StringifyIt, LogIt, GroupIt, ColumnIt, FlipIt, TupleIt, StringifyIt2, pipe, NotInIt, NotEqualIt

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

def createNormalizedLinksArray(pageTablePath, linksTablePath, outputPath):
    joined = SQLTableDefs.Join(pageTablePath, linksTablePath)
    array = Arrays.NormalizedLinksArray(outputPath)
    array.populate(LogIt(1000000)(joined.selectNormalizedLinks()))

def createAggregatedLinksTables(normalizedLinksArrayPath, tsnePath, inlinkTablePath, outlinkTablePath):
    tsne = SQLTableDefs.TSNETable(tsnePath)
    ids = ColumnIt(0)(tsne.selectAll())

    array = Arrays.NormalizedLinksArray(normalizedLinksArrayPath)
    array.filterRows(ids)

    outlinks = SQLTableDefs.AggregatedLinksTable(outlinkTablePath)
    array.sortByColumn(0)
    outlinks.create(pipe(array, LogIt(1000000), TupleIt, GroupIt))

    inlinks = SQLTableDefs.AggregatedLinksTable(inlinkTablePath)
    array.reverseColumns()
    array.sortByColumn(0)
    inlinks.create(pipe(array, LogIt(1000000), TupleIt, GroupIt))

def computePagerank(normalizedLinksArrayPath, pagerankPath):
    normLinks = Arrays.NormalizedLinksArray(normalizedLinksArrayPath)
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    pagerank.create()
    pagerank.populate(Pagerank.pagerank(TupleIt(normLinks)))

def createVocabulary(normalizedLinksArrayPath, pagerankPath, outputPath, wordCount=1000000):
    normLinks = Arrays.NormalizedLinksArray(normalizedLinksArrayPath)
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    ids = list(ColumnIt(0)(pagerank.selectIdsByDescendingRank(wordCount)))
    normLinks.filterRows(ids)

    w2v = Word2Vec()
    w2v.create(pipe(normLinks, StringifyIt2))
    w2v.save(outputPath)

def computeEmbeddings(normalizedLinksArrayPath, vocabularyPath, outputPath, iterations=10):
    normLinks = Arrays.NormalizedLinksArray(normalizedLinksArrayPath, shuffle=True)
    w2v = Word2Vec(vocabularyPath)
    ids = map(int, w2v.getVocab())
    normLinks.filterRows(ids)
    w2v.train(pipe(normLinks, StringifyIt2), iterations=iterations)
    w2v.save(outputPath, trim=True)

def computeEmbeddingsWithNode2Vec(normalizedLinksArrayPath, pagerankPath, outputPath, wordCount=1000000):
    normLinks = Arrays.NormalizedLinksArray(normalizedLinksArrayPath)
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    ids = list(ColumnIt(0)(pagerank.selectIdsByDescendingRank(wordCount)))
    normLinks.filterRows(ids)
    embeddingsTable = SQLTableDefs.EmbeddingsTable(outputPath)
    edges = LogIt(1000000, start="Reading edges...")(normLinks)
    embeddings = LogIt(10000)(Node2Vec(edges))
    embeddingsTable.create(embeddings)

def computeTSNE(embeddingsPath, pagerankPath, tsnePath, pointCount=10000):
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)

    ids = pipe(pagerank.selectIdsByDescendingRank(pointCount), StringifyIt, ColumnIt(0), list)
    w2v = Word2Vec(embeddingsPath)
    mappings = TSNE.train(w2v.getEmbeddings(ids))

    tsne = SQLTableDefs.TSNETable(tsnePath)
    tsne.create()
    tsne.populate(izip(ids, mappings[:, 0], mappings[:, 1]))

def computeHighDimensionalNeighbors(embeddingsPath, tsnePath, pagePath, outputPath, neighborsNo=10):
    joined = SQLTableDefs.Join(tsnePath, pagePath)

    data = list(joined.select_id_title_tsneX_tsneY())
    ids, titles = list(ColumnIt(0)(data)), list(ColumnIt(1)(data))
    w2v = Word2Vec(embeddingsPath)
    embeddings = w2v.getEmbeddings(imap(str, ids))

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
