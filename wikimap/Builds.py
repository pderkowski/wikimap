from Builder.Build import Build
import Jobs as J

English = Build([
    J.DownloadPagesDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'),
    J.DownloadLinksDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'),
    J.DownloadCategoryLinksDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz'),
    J.DownloadPagePropertiesDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page_props.sql.gz'),
    J.DownloadRedirectsDump(url='https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-redirect.sql.gz'),
    J.DownloadEvaluationDatasets(url='https://www.dropbox.com/s/d61802lo5n3gdra/datasets.tar.gz?dl=1'),
    J.ImportPageTable(),
    J.ImportLinksTable(),
    J.ImportPagePropertiesTable(),
    J.ImportCategoryLinksTable(),
    J.ImportRedirectsTable(),
    J.CreateLinkEdgesTable(),
    J.ComputePagerank(),
    J.ComputeEmbeddings(node_count=1000000, context_size=10),
    J.CreateTitleIndex(),
    J.EvaluateEmbeddings(use_word_mapping=False),
    J.ComputeTSNE(point_count=100000),
    J.ComputeHighDimensionalNeighbors(neighbors_count=10),
    J.ComputeLowDimensionalNeighbors(neighbors_count=10),
    J.CreateAggregatedLinksTables(),
    J.CreateWikimapDatapointsTable(),
    J.CreateWikimapCategoriesTable(depth=1),
    J.CreateZoomIndex(bucket_size=100)])

Polish = Build([
    J.DownloadPagesDump(url='https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-page.sql.gz'),
    J.DownloadLinksDump(url='https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-pagelinks.sql.gz'),
    J.DownloadCategoryLinksDump(url='https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-categorylinks.sql.gz'),
    J.DownloadPagePropertiesDump(url='https://dumps.wikimedia.org/plwiki/latest/plwiki-latest-page_props.sql.gz'),
    J.ImportPageTable(),
    J.ImportLinksTable(),
    J.ImportPagePropertiesTable(),
    J.ImportCategoryLinksTable(),
    J.CreateLinkEdgesTable(),
    J.ComputePagerank(),
    J.ComputeEmbeddings(node_count=1000000, context_size=10),
    J.ComputeTSNE(point_count=100000),
    J.ComputeHighDimensionalNeighbors(neighbors_count=10),
    J.ComputeLowDimensionalNeighbors(neighbors_count=10),
    J.CreateAggregatedLinksTables(),
    J.CreateWikimapDatapointsTable(),
    J.CreateWikimapCategoriesTable(depth=1),
    J.CreateZoomIndex(bucket_size=100)])

Builds = {
    "en": English,
    "pl": Polish
}
