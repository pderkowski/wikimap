from common import PathBase

paths = PathBase()
paths.add({
    'page'                      : 'page.db',
    'links'                     : 'links.db',
    'categoryLinks'             : 'categoryLinks.db',
    'pageProperties'            : 'pageProperties.db',
    'redirects'                 : 'redirects.db',
    'pagerank'                  : 'pagerank.db',
    'tsne'                      : 'tsne.db',
    'highDimensionalNeighbors'  : 'hdnn.db',
    'lowDimensionalNeighbors'   : 'ldnn.db',
    'wikimapPoints'             : 'wikimapPoints.db',
    'wikimapCategories'         : 'wikimapCategories.db',
    'metadata'                  : 'metadata.db',
    'zoomIndex'                 : 'zoom.idx',
    'termIndex'                 : 'term.idx',
    'pageSql'                   : 'page.sql.gz',
    'linksSql'                  : 'pagelinks.sql.gz',
    'categoryLinksSql'          : 'categorylinks.sql.gz',
    'pagePropertiesSql'         : 'pageprops.sql.gz',
    'redirectsSql'              : 'redirects.sql.gz',
    'linkEdges'                 : 'linkEdges.bin',
    'redirectEdges'             : 'redirectEdges.bin',
    'aggregatedInlinks'         : 'aggregatedInlinks.cdb',
    'aggregatedOutlinks'        : 'aggregatedOutlinks.cdb',
    'embeddings'                : 'embeddings.cdb',
    'embeddingIndex'            : 'embedding.idx',
    'embeddingReport'           : 'embeddingReport.txt'
})
