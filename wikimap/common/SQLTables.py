from SQLBase import TableProxy, Query

class WikimapPointsTable(TableProxy):
    def __init__(self, tablePath):
        super(WikimapPointsTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query(u"""
            CREATE TABLE wikipoints (
                wp_id                   INTEGER     NOT NULL    PRIMARY KEY,
                wp_title                TEXT        NOT NULL,
                wp_x                    REAL        NOT NULL,
                wp_y                    REAL        NOT NULL,
                wp_rank                 REAL        NOT NULL,
                wp_index                TEXT        NOT NULL    DEFAULT '',
                wp_high_dim_neighs      LIST        NOT NULL,
                wp_high_dim_dists       LIST        NOT NULL,
                wp_low_dim_neighs       LIST        NOT NULL,
                wp_low_dim_dists        LIST        NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query(u"""
            INSERT INTO wikipoints(
                wp_id,
                wp_title,
                wp_x,
                wp_y,
                wp_rank,
                wp_high_dim_neighs,
                wp_high_dim_dists,
                wp_low_dim_neighs,
                wp_low_dim_dists)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, "populating wikipoints table", logStart=True), values)

        self.execute(Query(u"CREATE UNIQUE INDEX title_idx ON wikipoints(wp_title);", "creating index title_idx in wikipoints table", logStart=True, logProgress=True))

    def updateIndex(self, values):
        self.executemany(Query(u"""
            UPDATE wikipoints
            SET
                wp_index = ?
            WHERE
                wp_id = ?
            """, "updating indices in wikipoints table", logStart=True), values)
        self.execute(Query("DROP INDEX IF EXISTS index_idx"))
        self.execute(Query("CREATE INDEX index_idx ON wikipoints(wp_index);", "creating index index_idx in wikipoints table", logStart=True, logProgress=True))

    def selectCoordsAndIds(self):
        return self.select(Query(u"SELECT wp_x, wp_y, wp_id FROM wikipoints"))

    def selectIds(self):
        return self.select(Query(u"SELECT wp_id FROM wikipoints"))

    def selectByTitle(self, title):
        return self.select(Query(u"SELECT * FROM wikipoints WHERE wp_title=?"), (title,))

    def selectByIds(self, ids):
        ids = list(ids)
        placeholders = '(' + ','.join(['?']*len(ids)) + ')'
        return self.select(Query(u"SELECT * FROM wikipoints WHERE wp_id IN " + placeholders), ids)

    def selectTitles(self):
        return self.select(Query(u"SELECT wp_title FROM wikipoints"))

    def selectTitlesAndRanks(self):
        return self.select(Query(u"SELECT wp_title, wp_rank FROM wikipoints"))

class WikimapCategoriesTable(TableProxy):
    def __init__(self, tablePath):
        super(WikimapCategoriesTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query(u"""
            CREATE TABLE wikicategories (
                wc_title        TEXT        NOT NULL,
                wc_page_ids     LIST        NOT NULL,
                wc_pages_count  INTEGER     NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query(u"INSERT INTO wikicategories VALUES (?,?,?)", "populating wikicategories table", logStart=True), values)
        self.execute(Query(u"CREATE UNIQUE INDEX title_idx ON wikicategories(wc_title);", "creating index title_idx in wikicategories table", logStart=True, logProgress=True))

    def selectByTitle(self, title):
        return self.select(Query(u"SELECT * FROM wikicategories WHERE wc_title=?"), (title,))

    def selectTitles(self):
        return self.select(Query(u"SELECT wc_title FROM wikicategories"))

    def selectTitlesAndSizes(self):
        return self.select(Query(u"SELECT wc_title, wc_pages_count FROM wikicategories"))
