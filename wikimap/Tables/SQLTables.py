from ..common.SQLBase import TableProxy, Query

class PageTable(TableProxy):
    def __init__(self, pageTablePath):
        super(PageTable, self).__init__(pageTablePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE page (
                page_id             INTEGER    NOT NULL                PRIMARY KEY,
                page_namespace      INTEGER    NOT NULL  DEFAULT '0',
                page_title          TEXT       NOT NULL  DEFAULT ''
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO page VALUES (?,?,?)", "populating page table", logStart=True), values)
        self.execute(Query("CREATE UNIQUE INDEX ns_title_idx ON page(page_namespace, page_title)", "creating index ns_title_idx in page table", logStart=True, logProgress=True))

    def select_id_title_of_articles(self):
        return self.select(Query("""
            SELECT page_id, page_title
            FROM page
            WHERE page_namespace=0"""))

    def select_id_title_of_categories(self):
        return self.select(Query("""
            SELECT page_id, page_title
            FROM page
            WHERE page_namespace=14"""))

    def select_id_of_articles(self):
        return self.select(Query("""
            SELECT page_id
            FROM page
            WHERE page_namespace = 0"""))

class CategoryLinksTable(TableProxy):
    def __init__(self, categoryLinksTablePath):
        super(CategoryLinksTable, self).__init__(categoryLinksTablePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE categorylinks (
                cl_from      INTEGER     NOT NULL    DEFAULT '0',
                cl_to        INTEGER     NOT NULL    DEFAULT ''
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO categorylinks VALUES (?,?)", "populating categorylinks table", logStart=True), values)
        self.execute(Query('CREATE INDEX from_idx ON categorylinks(cl_from);', "creating index from_idx in categorylinks table", logStart=True, logProgress=True))

class PagePropertiesTable(TableProxy):
    def __init__(self, pagePropertiesPath):
        super(PagePropertiesTable, self).__init__(pagePropertiesPath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE pageprops (
                pp_page        INTEGER     NOT NULL    DEFAULT '0',
                pp_propname    TEXT        NOT NULL    DEFAULT ''
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO pageprops VALUES (?,?)", "populating pageprops table", logStart=True), values)
        self.execute(Query('CREATE INDEX page_idx ON pageprops(pp_page);', "creating index page_idx in pageprops table", logStart=True, logProgress=True))
        self.execute(Query('CREATE INDEX propname_idx ON pageprops(pp_propname);', "creating index propname_idx in pageprops table", logStart=True, logProgress=True))

class RedirectsTable(TableProxy):
    def __init__(self, path):
        super(RedirectsTable, self).__init__(path)

    def create(self):
        self.execute(Query("""
            CREATE TABLE redirects (
                rd_from         INTEGER     NOT NULL  DEFAULT '0'   PRIMARY KEY,
                rd_namespace    INTEGER     NOT NULL  DEFAULT '0',
                rd_title        TEXT        NOT NULL  DEFAULT ''
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO redirects VALUES (?,?,?)", "populating redirects table", logStart=True), values)

class HighDimensionalNeighborsTable(TableProxy):
    def __init__(self, tablePath):
        super(HighDimensionalNeighborsTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query(u"""
            CREATE TABLE hdnn (
                hdnn_id                 INTEGER     NOT NULL    PRIMARY KEY,
                hdnn_neighbors_ids      LIST        NOT NULL,
                hdnn_neighbors_dists    LIST        NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query(u"INSERT INTO hdnn VALUES (?,?,?)", "populating hdnn table", logStart=True), values)

class LowDimensionalNeighborsTable(TableProxy):
    def __init__(self, tablePath):
        super(LowDimensionalNeighborsTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query(u"""
            CREATE TABLE ldnn (
                ldnn_id                 INTEGER     NOT NULL    PRIMARY KEY,
                ldnn_neighbors_ids      LIST        NOT NULL,
                ldnn_neighbors_dists    LIST        NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query(u"INSERT INTO ldnn VALUES (?,?,?)", "populating ldnn table", logStart=True), values)

class PagerankTable(TableProxy):
    def __init__(self, pagerankPath):
        super(PagerankTable, self).__init__(pagerankPath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE pagerank (
                pr_id               INTEGER     NOT NULL   PRIMARY KEY,
                pr_rank             REAL        NOT NULL,
                pr_order            INTEGER     NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO pagerank VALUES (?,?,?)", "populating pagerank table", logStart=True), values)
        self.execute(Query('CREATE INDEX rank_idx ON pagerank(pr_rank);', "creating index rank_idx in pagerank table", logStart=True, logProgress=True))
        self.execute(Query('CREATE UNIQUE INDEX order_idx ON pagerank(pr_order);', "creating index order_idx in pagerank table", logStart=True, logProgress=True))

    def select_ids_by_descending_rank(self, idsNo):
        query = Query("""
            SELECT
                pr_id
            FROM
                pagerank
            ORDER BY
                pr_order ASC
            LIMIT
                {}""".format(idsNo), 'selecting ids by descending rank', logProgress=True)

        return self.select(query)

    def select_id_rank(self, ids):
        ids = '(' + ','.join(map(str, ids)) + ')'
        return self.select(Query("""SELECT pr_id, pr_rank FROM pagerank WHERE pr_id IN {}""".format(ids), logProgress=True))

class TSNETable(TableProxy):
    def __init__(self, tsnePath):
        super(TSNETable, self).__init__(tsnePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE tsne (
                tsne_id         INTEGER     NOT NULL    PRIMARY KEY,
                tsne_x          REAL        NOT NULL,
                tsne_y          REAL        NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO tsne VALUES (?,?,?)", "populating tsne table", logStart=True), values)

    def selectAll(self):
        return self.select(Query("SELECT * FROM tsne"))

class Join(TableProxy):
    def __init__(self, *tables):
        super(Join, self).__init__(*tables)

    def select_link_edges(self):
        query = Query("""
            SELECT
                pl_from, page_id
            FROM
                links,
                page
            WHERE
                pl_namespace = page_namespace
            AND pl_title = page_title
            ORDER BY
                pl_namespace ASC,
                pl_title ASC""", "selecting link edges", logProgress=True)

        return self.select(query)

    def selectRedirectEdges(self):
        query = Query("""
            SELECT
                rd_from, page_id
            FROM
                redirects,
                page
            WHERE
                rd_namespace = 0
            AND page_namespace = 0
            AND rd_title = page_title""", "selecting redirect edges", logProgress=True)

        return self.select(query)

    def selectWikimapPoints(self):
        query = Query("""
            SELECT
                page_id,
                page_title,
                tsne_x,
                tsne_y,
                pr_rank,
                hdnn_neighbors_ids,
                hdnn_neighbors_dists,
                ldnn_neighbors_ids,
                ldnn_neighbors_dists
            FROM
                tsne,
                page,
                hdnn,
                ldnn,
                pagerank
            WHERE
                page_id = tsne_id
            AND page_id = hdnn_id
            AND page_id = ldnn_id
            AND page_id = pr_id
            ORDER BY
                pr_rank DESC
            """, "selecting data for wikipoints", logProgress=True)

        return self.select(query)

    def select_hidden_categories(self):
        query = Query("""
            SELECT
                page_id
            FROM
                page,
                pageprops
            WHERE
                page_id = pp_page
            AND pp_propname = 'hiddencat'""", "selecting hidden categories", logStart=True, logProgress=True)
        return self.select(query)

    def select_id_category_name(self):
        query = Query("""
            SELECT
                cl_from,
                page_title
            FROM
                categorylinks,
                tsne,
                page
            WHERE
                tsne_id = cl_from
            AND cl_to = page_id""", "selecting nodes for wikicategories")

        return self.select(query)

    def select_id_category_id_of_tsne_points(self):
        query = Query("""
            SELECT
                cl_from,
                cl_to
            FROM
                categorylinks,
                tsne
            WHERE
                tsne_id = cl_from""", "selecting nodes for wikicategories")

        return self.select(query)

    # ONLY LINKS BETWEEN CATEGORIES, NOT BETWEEN A PAGE AND A CATEGORY
    def select_links_between_categories(self):
        query = Query("""
            SELECT
                cl_from,
                cl_to
            FROM
                categorylinks,
                page NOT INDEXED
            WHERE
                cl_from = page_id
            AND page_namespace = 14""", "selecting links for wikicategories")

        return self.select(query)

    def select_links_between_articles_and_categories(self):
        query = Query("""
            SELECT
                cl_from,
                cl_to
            FROM
                categorylinks,
                page NOT INDEXED
            WHERE
                cl_from = page_id
            AND page_namespace = 0""")

        return self.select(query)

    def select_id_title_tsneX_tsneY(self):
        query = Query("""
            SELECT
                page_id,
                page_title,
                tsne_x,
                tsne_y
            FROM
                page,
                tsne
            WHERE
                page_id = tsne_id""", logProgress=True)

        return self.select(query)

    def select_id_x_y_byRank(self):
        query = Query("""
            SELECT
                wp_id,
                wp_x,
                wp_y
            FROM
                wikipoints,
                pagerank
            WHERE
                wp_id = pr_id
            ORDER BY
                pr_rank DESC
            """, logProgress=True)

        return self.select(query)

    def select_disambiguation_pages(self):
        query = Query("""
            SELECT
                cl_from
            FROM
                page,
                categorylinks
            WHERE
                page_id = cl_to
            AND page_title = 'Category:Disambiguation_pages'
            """, logProgress=True)

        return self.select(query)
