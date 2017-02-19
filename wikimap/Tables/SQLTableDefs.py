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

class LinksTable(TableProxy):
    def __init__(self, linksTablePath):
        super(LinksTable, self).__init__(linksTablePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE links (
                pl_from             INTEGER    NOT NULL  DEFAULT '0',
                pl_namespace        INTEGER    NOT NULL  DEFAULT '0',
                pl_title            TEXT       NOT NULL  DEFAULT '',
                pl_from_namespace   INTEGER    NOT NULL  DEFAULT '0'
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO links VALUES (?,?,?,?)", "populating links table", logStart=True), values)
        self.execute(Query("CREATE INDEX from_id_idx ON links(pl_from);", "creating index from_id_idx in links table", logStart=True, logProgress=True))
        self.execute(Query("CREATE INDEX ns_title_idx ON links(pl_namespace, pl_title);", "creating index ns_title_idx in links table", logStart=True, logProgress=True))

class CategoryLinksTable(TableProxy):
    def __init__(self, categoryLinksTablePath):
        super(CategoryLinksTable, self).__init__(categoryLinksTablePath)

    def create(self):
        self.execute(Query("""
            CREATE TABLE categorylinks (
                cl_from      INTEGER     NOT NULL    DEFAULT '0',
                cl_to        TEXT        NOT NULL    DEFAULT ''
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

class Join(TableProxy):
    def __init__(self, *tables):
        super(Join, self).__init__(*tables)

    def selectNormalizedLinks(self):
        query = Query("""
            SELECT
                *
            FROM
                (SELECT
                    pl_from, page_id
                FROM
                    links,
                    page
                WHERE
                    pl_namespace = page_namespace
                AND pl_title = page_title
                ORDER BY
                    pl_namespace ASC,
                    pl_title ASC)
            ORDER BY
                pl_from ASC""", "selecting normalized links", logProgress=True)

        return self.select(query)

    def selectWikimapPoints(self):
        query = Query("""
            SELECT
                page_id,
                page_title,
                tsne_x,
                tsne_y,
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

    def selectHiddenCategories(self):
        query = Query("""
            SELECT
                page_title
            FROM
                page,
                pageprops
            WHERE
                page_id = pp_page
            AND pp_propname = 'hiddencat'""", "selecting hidden categories", logStart=True, logProgress=True)
        return self.select(query)

    def select_id_category(self):
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
    def selectCategoryLinks(self):
        query = Query("""
            SELECT
                page_title,
                cl_to
            FROM
                categorylinks,
                page
            WHERE
                cl_from = page_id
            AND page_namespace = 14""", "selecting links for wikicategories")

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
