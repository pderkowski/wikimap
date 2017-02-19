from ..Utils import LogIt, ColumnIt, NotInIt, pipe
from EdgeArray import EdgeArray
import TableImporter
import SQLTableDefs

def createPageTable(pagePath, outputPath):
    source = TableImporter.PageTable(pagePath)
    table = SQLTableDefs.PageTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createLinksTable(linksPath, outputPath):
    source = TableImporter.LinksTable(linksPath)
    table = SQLTableDefs.LinksTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createPagePropertiesTable(pagePropertiesPath, outputPath):
    source = TableImporter.PagePropertiesTable(pagePropertiesPath)
    table = SQLTableDefs.PagePropertiesTable(outputPath)
    table.create()
    table.populate(LogIt(1000000)(source.read()))

def createCategoryLinksTable(categoryLinksPath, pageTablePath, pagePropertiesTablePath, outputPath):
    joined = SQLTableDefs.Join(pageTablePath, pagePropertiesTablePath)
    hiddenCategories = frozenset(ColumnIt(0)(joined.selectHiddenCategories()))

    table = SQLTableDefs.CategoryLinksTable(outputPath)
    table.create()

    source = TableImporter.CategoryLinksTable(categoryLinksPath)
    table.populate(pipe(source.read(), NotInIt(hiddenCategories, 1), LogIt(1000000)))

def createEdgeArray(pagesPath, linksPath, outputPath):
    joined = SQLTableDefs.Join(pagesPath, linksPath)
    edges = EdgeArray(outputPath)
    edges.populate(LogIt(1000000)(joined.selectNormalizedLinks()))
