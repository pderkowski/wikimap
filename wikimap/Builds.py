from Builder.Build import Build
import Jobs as J

def english():
    return Build([
        J.DownloadPagesDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'),
        J.DownloadLinksDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'),
        J.DownloadCategoryLinksDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz'),
        J.DownloadPagePropertiesDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page_props.sql.gz'),
        J.DownloadRedirectsDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-redirect.sql.gz'),
        J.DownloadEvaluationDatasets(url='https://www.dropbox.com/s/d61802lo5n3gdra/datasets.tar.gz?dl=1'),
        J.ImportPageTable(),
        J.ImportPagePropertiesTable(),
        J.ImportCategoryLinksTable(),
        J.ImportRedirectsTable(),
        J.CreateLinkEdgesTable(),
        J.ComputePagerank(),
        J.ComputeEmbeddings(),
        J.CreateTitleIndex(),
        J.EvaluateEmbeddings(),
        J.ComputeTSNE(),
        J.ComputeHighDimensionalNeighbors(),
        J.ComputeLowDimensionalNeighbors(),
        J.CreateAggregatedLinksTables(),
        J.CreateWikimapDatapointsTable(),
        J.CreateWikimapCategoriesTable(),
        J.CreateZoomIndex()])

def polish():
    return Build([
        J.DownloadPagesDump(url='https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-page.sql.gz'),
        J.DownloadLinksDump(url='https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-pagelinks.sql.gz'),
        J.DownloadCategoryLinksDump(url='https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-categorylinks.sql.gz'),
        J.DownloadPagePropertiesDump(url='https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-page_props.sql.gz'),
        J.ImportPageTable(),
        J.ImportPagePropertiesTable(),
        J.ImportCategoryLinksTable(),
        J.CreateLinkEdgesTable(),
        J.ComputePagerank(),
        J.ComputeEmbeddings(),
        J.ComputeTSNE(),
        J.ComputeHighDimensionalNeighbors(),
        J.ComputeLowDimensionalNeighbors(),
        J.CreateAggregatedLinksTables(),
        J.CreateWikimapDatapointsTable(),
        J.CreateWikimapCategoriesTable(),
        J.CreateZoomIndex()])

Builds = {
    "en": english(),
    "pl": polish()
}
