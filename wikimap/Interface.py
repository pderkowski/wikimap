import urllib
import Utils
import SQL
import Tools
import Pagerank
import Word2Vec
import TSNE
import logging
import itertools
import codecs
from Utils import StringifyIt, LogIt, DeferIt, GroupIt, JoinIt, ColumnIt, pipe

def createPageTable(pageSql, outputPath):
    source = Tools.TableImporter(pageSql, Tools.getPageRecords, "page")
    table = SQL.PageTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createLinksTable(linksSql, outputPath):
    source = Tools.TableImporter(linksSql, Tools.getLinksRecords, "pagelinks")
    table = SQL.LinksTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createCategoryTable(categorySql, outputPath):
    source = Tools.TableImporter(categorySql, Tools.getCategoryRecords, "category")
    table = SQL.CategoryTable(outputPath)
    table.create()
    table.populate(source.read())

def createPagePropertiesTable(pagePropertiesSql, outputPath):
    source = Tools.TableImporter(pagePropertiesSql, Tools.getPagePropertiesRecords, "page_props")
    table = SQL.PagePropertiesTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createCategoryLinksTable(categoryLinksSql, outputPath):
    source = Tools.TableImporter(categoryLinksSql, Tools.getCategoryLinksRecords, "categorylinks")
    table = SQL.CategoryLinksTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createNormalizedLinksTable(pageTable, linksTable, outputPath):
    source = SQL.Join(pageTable, linksTable)
    table = SQL.NormalizedLinksTable(outputPath)
    table.create()
    table.populate(source.selectNormalizedLinks())

def computePagerank(normalizedLinksPath, pagerankPath):
    normLinks = SQL.NormalizedLinksTable(normalizedLinksPath)
    pagerank = SQL.PagerankTable(pagerankPath)
    pagerank.create()
    pagerank.populate(Pagerank.pagerank(pipe(normLinks.selectAll(), StringifyIt, JoinIt)))

def computeVocabulary(normalizedLinksPath, outputPath):
    normLinks = SQL.NormalizedLinksTable(normalizedLinksPath)
    Word2Vec.buildVocabulary(pipe(normLinks.selectAll, DeferIt, StringifyIt), outputPath)

def computeEmbeddings(normalizedLinksPath, vocabularyPath, outputPath):
    normLinks = SQL.NormalizedLinksTable(normalizedLinksPath)
    Word2Vec.train(pipe(normLinks.selectAll, DeferIt, StringifyIt), vocabularyPath, outputPath)

def computeTSNE(embeddingsPath, pagerankPath, tsnePath, pagesNo=10000):
    pagerank = SQL.PagerankTable(pagerankPath)
    tsne = SQL.TSNETable(tsnePath)
    tsne.create()

    ids = pipe(pagerank.selectIdsByDescendingRank(pagesNo), StringifyIt, ColumnIt(0), list)
    mappings = TSNE.train(Word2Vec.getEmbeddings(embeddingsPath, ids))
    tsne.populate(itertools.izip(ids, mappings[:,0], mappings[:,1], xrange(mappings.shape[0])))

def selectVisualizedPoints(tsnePath, pagesPath, outputPath):
    source = SQL.Join(tsnePath, pagesPath)

    with codecs.open(outputPath, 'w', encoding='utf8') as output:
        for row in source.selectVisualizedPoints():
            output.write(u'{} {} {} {}\n'.format(row[0], row[1], row[2], row[3]))

def selectVisualizedCategories(categoryLinksPath, categoryPath, pagesPath, tsnePath, pagePropertiesPath, outputPath):
    source = SQL.Join(categoryLinksPath, pagesPath, tsnePath, categoryPath, pagePropertiesPath)

    with codecs.open(outputPath, 'w' ,encoding='utf8') as output:
        for row in pipe(source.selectVisualizedCategories(), GroupIt, StringifyIt, JoinIt):
            output.write(row)


# def computeSimilar(embeddingsPath, output):
#     con = sqlite3.connect(output)
#     con.execute("""
#         CREATE TABLE similar (
#             sim_id      INTEGER     NOT NULL    PRIMARY KEY,
#             sim_list    BLOB        NOT NULL
#         );""")

#     def extractValues(it):
#         (id_, simList) = it
#         return (id_, sqlite3.Binary(Utils.listToBinary(simList)))

#     con.executemany("INSERT INTO similar VALUES (?, ?)", itertools.imap(extractValues, Link2Vec.iterateSimilar(embeddingsPath)))
#     con.commit()


# def computeWordVectorNeighbors(modelPath, outputPath):