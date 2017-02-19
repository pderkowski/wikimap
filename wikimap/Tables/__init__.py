from ..common import SQLTableDefs
from ..Utils import LogIt
from EdgeArray import EdgeArray

def createEdgeArray(pagesPath, linksPath, outputPath):
    joined = SQLTableDefs.Join(pagesPath, linksPath)
    edges = EdgeArray(outputPath)
    edges.populate(LogIt(1000000)(joined.selectNormalizedLinks()))
