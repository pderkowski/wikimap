from Job import Job
import Interface
import Utils
from common.Paths import paths as Path

class Build(object):
    def __init__(self):
        pageUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
        linksUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'
        categoryLinksUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz'
        pagePropertiesUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page_props.sql.gz'

        pageSql = Path['pageSql']
        linksSql = Path['linksSql']
        categoryLinksSql = Path['categoryLinksSql']
        pagePropertiesSql = Path['pagePropertiesSql']

        page = Path['page']
        links = Path['links']
        categoryLinks = Path['categoryLinks']
        pageProperties = Path['pageProperties']
        normalizedLinksArray = Path['normalizedLinksArray']
        aggregatedInlinks = Path['aggregatedInlinks']
        aggregatedOutlinks = Path['aggregatedOutlinks']

        pagerank = Path['pagerank']
        tsne = Path['tsne']
        highDimensionalNeighbors = Path['highDimensionalNeighbors']
        lowDimensionalNeighbors = Path['lowDimensionalNeighbors']
        wikimapPoints = Path['wikimapPoints']
        wikimapCategories = Path['wikimapCategories']
        metadata = Path['metadata']
        zoomIndex = Path['zoomIndex']
        termIndex = Path['termIndex']

        vocabulary = Path['vocabulary']
        embeddings = Path['embeddings']
        vocabularyArtifacts = Path['vocabularyArtifacts']
        embeddingsArtifacts = Path['embeddingsArtifacts']

        embeddingsTable = Path['embeddings2']

        jobs = []
        jobs.append(Job('DOWNLOAD PAGE TABLE', Utils.download(pageUrl), inputs=[], outputs=[pageSql]))
        jobs.append(Job('DOWNLOAD LINKS TABLE', Utils.download(linksUrl), inputs=[], outputs=[linksSql]))
        jobs.append(Job('DOWNLOAD CATEGORY LINKS TABLE', Utils.download(categoryLinksUrl), inputs=[], outputs=[categoryLinksSql]))
        jobs.append(Job('DOWNLOAD PAGE PROPERTIES TABLE', Utils.download(pagePropertiesUrl), inputs=[], outputs=[pagePropertiesSql]))

        jobs.append(Job('CREATE PAGE TABLE', Interface.createPageTable, inputs=[pageSql], outputs=[page]))
        jobs.append(Job('CREATE LINKS TABLE', Interface.createLinksTable, inputs=[linksSql], outputs=[links]))
        jobs.append(Job('CREATE PAGE PROPERTIES TABLE', Interface.createPagePropertiesTable, inputs=[pagePropertiesSql], outputs=[pageProperties]))
        jobs.append(Job('CREATE CATEGORY LINKS TABLE', Interface.createCategoryLinksTable, inputs=[categoryLinksSql, page, pageProperties], outputs=[categoryLinks]))

        jobs.append(Job('CREATE NORMALIZED LINKS ARRAY', Interface.createNormalizedLinksArray, inputs=[page, links], outputs=[normalizedLinksArray]))
        jobs.append(Job('COMPUTE PAGERANK', Interface.computePagerank, inputs=[normalizedLinksArray], outputs=[pagerank]))

        jobs.append(Job('CREATE WORD VOCABULARY', Interface.createVocabulary, inputs=[normalizedLinksArray, pagerank], outputs=[vocabulary], artifacts=[vocabularyArtifacts], wordCount=1000000))

        jobs.append(Job('COMPUTE WORD EMBEDDINGS', Interface.computeEmbeddings, inputs=[normalizedLinksArray, vocabulary], outputs=[embeddings], artifacts=[embeddingsArtifacts], iterations=10))
        jobs.append(Job('COMPUTE EMBEDDINGS WITH NODE2VEC', Interface.computeEmbeddingsWithNode2Vec, inputs=[normalizedLinksArray, pagerank], outputs=[embeddingsTable], wordCount=30000))
        jobs.append(Job('COMPUTE TSNE', Interface.computeTSNE, inputs=[embeddings, pagerank], outputs=[tsne], pointCount=100000))
        jobs.append(Job('COMPUTE HIGH DIMENSIONAL NEIGHBORS', Interface.computeHighDimensionalNeighbors, inputs=[embeddings, tsne, page], outputs=[highDimensionalNeighbors]))
        jobs.append(Job('COMPUTE LOW DIMENSIONAL NEIGHBORS', Interface.computeLowDimensionalNeighbors, inputs=[tsne, page], outputs=[lowDimensionalNeighbors]))

        jobs.append(Job('CREATE AGGREGATED LINKS TABLES', Interface.createAggregatedLinksTables, inputs=[normalizedLinksArray, tsne], outputs=[aggregatedInlinks, aggregatedOutlinks]))
        jobs.append(Job('CREATE WIKIMAP DATAPOINTS TABLE', Interface.createWikimapPointsTable, inputs=[tsne, page, highDimensionalNeighbors, lowDimensionalNeighbors, pagerank], outputs=[wikimapPoints]))
        jobs.append(Job('CREATE WIKIMAP CATEGORIES TABLE', Interface.createWikimapCategoriesTable, inputs=[categoryLinks, page, tsne], outputs=[wikimapCategories], depth=1))
        jobs.append(Job('CREATE ZOOM INDEX', Interface.createZoomIndex, inputs=[wikimapPoints, pagerank], outputs=[zoomIndex, metadata], bucketSize=100))
        jobs.append(Job('CREATE TERM INDEX', Interface.createTermIndex, inputs=[wikimapPoints, wikimapCategories], outputs=[termIndex]))

        self.jobs = jobs

    def __iter__(self):
        return iter(self.jobs)

    def __getitem__(self, n):
        return self.jobs[n]

    def setBasePath(self, path):
        Path.base = path
