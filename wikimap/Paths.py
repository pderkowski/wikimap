from common.Paths import paths, resolve

paths.add({
    'pageSql'               : 'page.sql.gz',
    'linksSql'              : 'pagelinks.sql.gz',
    'categorySql'           : 'category.sql.gz',
    'categoryLinksSql'      : 'categorylinks.sql.gz',
    'pagePropertiesSql'     : 'pageprops.sql.gz',
    'vocabulary'            : 'vocabulary',
    'embeddings'            : 'embeddings',
    'vocabularyArtifacts'   : ['vocabulary.syn0_lockf.npy', 'vocabulary.syn0.npy', 'vocabulary.syn1neg.npy'],
    'embeddingsArtifacts'   : ['embeddings.syn0_lockf.npy', 'embeddings.syn0.npy', 'embeddings.syn1neg.npy'],
    'degrees'               : 'degrees.db',
    'degreePlot'            : 'degree.svg'
})
