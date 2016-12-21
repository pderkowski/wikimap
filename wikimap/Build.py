from Job import Job
import Interface
import Utils

class Build(object):
    def __init__(self):
        pageUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
        linksUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'
        categoryUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-category.sql.gz'
        categoryLinksUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz'
        pagePropertiesUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page_props.sql.gz'
        pageSql = 'page.sql.gz'
        linksSql = 'pagelinks.sql.gz'
        categorySql = 'category.sql.gz'
        categoryLinksSql = 'categorylinks.sql.gz'
        pagePropertiesSql = 'pageprops.sql.gz'
        page = 'page.db'
        links = 'links.db'
        category = 'category.db'
        categoryLinks = 'categoryLinks.db'
        pageProperties = 'pageProperties.db'
        normalizedLinks = 'normalizedLinks.db'
        pagerank = 'pagerank.db'
        vocabulary = 'vocabulary'
        vocabularyArtifacts = [vocabulary+a for a in ['.syn0_lockf.npy', '.syn0.npy', '.syn1neg.npy']]
        embeddings = 'embeddings'
        embeddingsArtifacts = [embeddings+a for a in ['.syn0_lockf.npy', '.syn0.npy', '.syn1neg.npy']]
        tsne = 'tsne.db'
        highDimensionalNeighbors = 'hdnn.db'
        lowDimensionalNeighbors = 'ldnn.db'
        wikimapPoints = 'wikimapPoints.db'
        wikimapCategories = 'wikimapCategories.db'
        zoomIndex = 'zoom.idx'
        metadata = 'metadata.db'

        jobs = []
        jobs.append(Job('DOWNLOAD PAGE TABLE', Utils.download(pageUrl), inputs=[], outputs=[pageSql]))
        jobs.append(Job('DOWNLOAD LINKS TABLE', Utils.download(linksUrl), inputs=[], outputs=[linksSql]))
        jobs.append(Job('DOWNLOAD CATEGORY TABLE', Utils.download(categoryUrl), inputs=[], outputs=[categorySql]))
        jobs.append(Job('DOWNLOAD CATEGORY LINKS TABLE', Utils.download(categoryLinksUrl), inputs=[], outputs=[categoryLinksSql]))
        jobs.append(Job('DOWNLOAD PAGE PROPERTIES TABLE', Utils.download(pagePropertiesUrl), inputs=[], outputs=[pagePropertiesSql]))

        jobs.append(Job('CREATE PAGE TABLE', Interface.createPageTable, inputs=[pageSql], outputs=[page]))
        jobs.append(Job('CREATE LINKS TABLE', Interface.createLinksTable, inputs=[linksSql], outputs=[links]))
        jobs.append(Job('CREATE CATEGORY TABLE', Interface.createCategoryTable, inputs=[categorySql], outputs=[category]))
        jobs.append(Job('CREATE CATEGORY LINKS TABLE', Interface.createCategoryLinksTable, inputs=[categoryLinksSql], outputs=[categoryLinks]))
        jobs.append(Job('CREATE PAGE PROPERTIES TABLE', Interface.createPagePropertiesTable, inputs=[pagePropertiesSql], outputs=[pageProperties]))
        jobs.append(Job('CREATE NORMALIZED LINKS TABLE', Interface.createNormalizedLinksTable, inputs=[page, links], outputs=[normalizedLinks]))

        jobs.append(Job('COMPUTE PAGERANK', Interface.computePagerank, inputs=[normalizedLinks], outputs=[pagerank]))
        jobs.append(Job('COMPUTE WORD VOCABULARY', Interface.computeVocabulary, inputs=[normalizedLinks], outputs=[vocabulary], artifacts=vocabularyArtifacts))
        jobs.append(Job('COMPUTE WORD EMBEDDINGS', Interface.computeEmbeddings, inputs=[normalizedLinks, vocabulary], outputs=[embeddings], artifacts=embeddingsArtifacts))
        jobs.append(Job('COMPUTE TSNE', Interface.computeTSNE, inputs=[embeddings, pagerank], outputs=[tsne], pointCount=100000))
        jobs.append(Job('COMPUTE HIGH DIMENSIONAL NEIGHBORS', Interface.computeHighDimensionalNeighbors, inputs=[embeddings, tsne, page], outputs=[highDimensionalNeighbors]))
        jobs.append(Job('COMPUTE LOW DIMENSIONAL NEIGHBORS', Interface.computeLowDimensionalNeighbors, inputs=[tsne, page], outputs=[lowDimensionalNeighbors]))

        jobs.append(Job('CREATE WIKIMAP DATAPOINTS TABLE', Interface.createWikimapPointsTable, inputs=[tsne, page, highDimensionalNeighbors, lowDimensionalNeighbors, pagerank], outputs=[wikimapPoints]))
        jobs.append(Job('CREATE WIKIMAP CATEGORIES TABLE', Interface.createWikimapCategoriesTable, inputs=[categoryLinks, category, page, tsne, pageProperties], outputs=[wikimapCategories]))
        jobs.append(Job('CREATE ZOOM INDEX', Interface.createZoomIndex, inputs=[wikimapPoints, pagerank], outputs=[zoomIndex, metadata], bucketSize=100))

        self.jobs = jobs
        self.results = [wikimapPoints, wikimapCategories, zoomIndex, metadata]

    def __iter__(self):
        return iter(self.jobs)

    def __getitem__(self, n):
        return self.jobs[n]
