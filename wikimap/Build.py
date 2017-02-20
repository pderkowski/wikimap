from Job import Job
import Interface
import Utils
from Paths import paths as Path

class Build(object):
    def __init__(self):
        pageUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
        linksUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'
        categoryLinksUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz'
        pagePropertiesUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page_props.sql.gz'
        redirectsUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-redirect.sql.gz'

        pageSql = Path['pageSql']
        linksSql = Path['linksSql']
        categoryLinksSql = Path['categoryLinksSql']
        pagePropertiesSql = Path['pagePropertiesSql']
        redirectsSql = Path['redirectsSql']

        page = Path['page']
        links = Path['links']
        categoryLinks = Path['categoryLinks']
        pageProperties = Path['pageProperties']
        redirects = Path['redirects']
        linkEdges = Path['linkEdges']
        redirectEdges = Path['redirectEdges']
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
        embeddings = Path['embeddings']
        embeddingIndex = Path['embeddingIndex']
        embeddingReport = Path['embeddingReport']

        jobs = []
        jobs.append(Job('DOWNLOAD PAGE TABLE', Utils.download(pageUrl), inputs=[], outputs=[pageSql]))
        jobs.append(Job('DOWNLOAD LINKS TABLE', Utils.download(linksUrl), inputs=[], outputs=[linksSql]))
        jobs.append(Job('DOWNLOAD CATEGORY LINKS TABLE', Utils.download(categoryLinksUrl), inputs=[], outputs=[categoryLinksSql]))
        jobs.append(Job('DOWNLOAD PAGE PROPERTIES TABLE', Utils.download(pagePropertiesUrl), inputs=[], outputs=[pagePropertiesSql]))
        jobs.append(Job('DOWNLOAD REDIRECTS TABLE', Utils.download(redirectsUrl), inputs=[], outputs=[redirectsSql]))

        jobs.append(Job('CREATE PAGE TABLE', Interface.createPageTable, inputs=[pageSql], outputs=[page]))
        jobs.append(Job('CREATE LINKS TABLE', Interface.createLinksTable, inputs=[linksSql], outputs=[links]))
        jobs.append(Job('CREATE PAGE PROPERTIES TABLE', Interface.createPagePropertiesTable, inputs=[pagePropertiesSql], outputs=[pageProperties]))
        jobs.append(Job('CREATE CATEGORY LINKS TABLE', Interface.createCategoryLinksTable, inputs=[categoryLinksSql, page, pageProperties], outputs=[categoryLinks]))
        jobs.append(Job('CREATE REDIRECTS TABLE', Interface.createRedirectsTable, inputs=[redirectsSql], outputs=[redirects]))

        jobs.append(Job('CREATE LINK EDGES TABLE', Interface.createLinkEdgesTable, inputs=[links, page], outputs=[linkEdges]))
        jobs.append(Job('CREATE REDIRECT EDGES TABLE', Interface.createRedirectEdgesTable, inputs=[redirects, page], outputs=[redirectEdges]))

        jobs.append(Job('COMPUTE PAGERANK', Interface.computePagerank, inputs=[linkEdges], outputs=[pagerank]))
        jobs.append(Job('COMPUTE EMBEDDINGS WITH NODE2VEC', Interface.computeEmbeddingsWithNode2Vec, inputs=[linkEdges, pagerank], outputs=[embeddings], wordCount=1000000))
        jobs.append(Job('CREATE EMBEDDING INDEX', Interface.createEmbeddingIndex, inputs=[embeddings, page, redirectEdges], outputs=[embeddingIndex]))
        jobs.append(Job('EVALUATE EMBEDDINGS', Interface.evaluateEmbeddings, inputs=[embeddings, embeddingIndex], outputs=[embeddingReport]))

        jobs.append(Job('COMPUTE TSNE', Interface.computeTSNE, inputs=[embeddings, pagerank], outputs=[tsne], pointCount=100000))
        jobs.append(Job('COMPUTE HIGH DIMENSIONAL NEIGHBORS', Interface.computeHighDimensionalNeighbors, inputs=[embeddings, tsne, page], outputs=[highDimensionalNeighbors]))
        jobs.append(Job('COMPUTE LOW DIMENSIONAL NEIGHBORS', Interface.computeLowDimensionalNeighbors, inputs=[tsne, page], outputs=[lowDimensionalNeighbors]))

        jobs.append(Job('CREATE AGGREGATED LINKS TABLES', Interface.createAggregatedLinksTables, inputs=[linkEdges, tsne], outputs=[aggregatedInlinks, aggregatedOutlinks]))
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
