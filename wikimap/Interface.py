import SQLTableDefs
import Tools
import Pagerank
import Word2Vec
import TSNE
import NearestNeighbors
from itertools import imap, izip
from Utils import StringifyIt, LogIt, DeferIt, GroupIt, JoinIt, ColumnIt, UnconsIt, pipe

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
    pagerank.populate(Pagerank.pagerank(pipe(normLinks.selectAll(), StringifyIt, JoinIt)))

def computeVocabulary(normalizedLinksPath, outputPath):
    normLinks = SQLTableDefs.NormalizedLinksTable(normalizedLinksPath)
    Word2Vec.buildVocabulary(pipe(normLinks.selectAll, DeferIt, StringifyIt), outputPath)

def computeEmbeddings(normalizedLinksPath, vocabularyPath, outputPath):
    normLinks = SQLTableDefs.NormalizedLinksTable(normalizedLinksPath)
    Word2Vec.train(pipe(normLinks.selectAll, DeferIt, StringifyIt), vocabularyPath, outputPath)

def computeTSNE(embeddingsPath, pagerankPath, tsnePath, pagesNo=10000):
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    tsne = SQLTableDefs.TSNETable(tsnePath)
    tsne.create()

    ids = pipe(pagerank.selectIdsByDescendingRank(pagesNo), StringifyIt, ColumnIt(0), list)
    mappings = TSNE.train(Word2Vec.getEmbeddings(embeddingsPath, ids))
    tsne.populate(izip(ids, mappings[:, 0], mappings[:, 1], xrange(mappings.shape[0])))

def computeHighDimensionalNeighbors(embeddingsPath, pagerankPath, outputPath, neighborsNo=10, pagesNo=10000):
    pagerank = SQLTableDefs.PagerankTable(pagerankPath)
    ids = pipe(pagerank.selectIdsByDescendingRank(pagesNo), StringifyIt, ColumnIt(0), list)
    embeddings = Word2Vec.getEmbeddings(embeddingsPath, ids)

    table = SQLTableDefs.HighDimensionalNeighborsTable(outputPath)
    table.create()

    distances, indices = NearestNeighbors.computeNearestNeighbors(embeddings, neighborsNo)
    table.populate(izip(imap(int, ids), imap(lambda a: [int(ids[i]) for i in a], indices), imap(list, distances)))

def computeLowDimensionalNeighbors(tsnePath, outputPath, neighborsNo=10):
    tsne = SQLTableDefs.TSNETable(tsnePath)
    ids = pipe(tsne.selectAll(), ColumnIt(0), list)
    points = pipe(tsne.selectAll(), ColumnIt(1, 2))

    table = SQLTableDefs.LowDimensionalNeighborsTable(outputPath)
    table.create()

    distances, indices = NearestNeighbors.computeNearestNeighbors(points, neighborsNo)
    table.populate(izip(ids, imap(lambda a: [ids[i] for i in a], indices), imap(list, distances)))

def createWikimapPointsTable(tsnePath, pagesPath, hdnnPath, ldnnPath, outputPath):
    data = SQLTableDefs.Join(tsnePath, pagesPath, hdnnPath, ldnnPath)

    table = SQLTableDefs.WikimapPointsTable(outputPath)
    table.create()

    table.populate(data.selectWikimapPoints())

def createWikimapCategoriesTable(categoryLinksPath, categoryPath, pagesPath, tsnePath, pagePropertiesPath, outputPath):
    data = SQLTableDefs.Join(categoryLinksPath, pagesPath, tsnePath, categoryPath, pagePropertiesPath)

    table = SQLTableDefs.WikimapCategoriesTable(outputPath)
    table.create()

    table.populate(pipe(data.selectWikimapCategories(), GroupIt, UnconsIt))
