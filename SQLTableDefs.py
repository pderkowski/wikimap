from SQLBase import TableProxy, Query

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
                wp_xindex               INTEGER     NOT NULL    DEFAULT '0', -- filled by wikimap_ui
                wp_yindex               INTEGER     NOT NULL    DEFAULT '0', -- filled by wikimap_ui
                wp_zindex               INTEGER     NOT NULL    DEFAULT '0', -- filled by wikimap_ui
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
                wp_high_dim_neighs,
                wp_high_dim_dists,
                wp_low_dim_neighs,
                wp_low_dim_dists)
            VALUES (?,?,?,?,?,?,?,?)
        """, "populating wikipoints table", logStart=True), values)

        self.execute(Query(u"CREATE UNIQUE INDEX title_idx ON wikipoints(wp_title);", "creating index title_idx in wikipoints table", logStart=True, logProgress=True))

    def updateIndices(self, values):
        self.executemany(Query(u"""
            UPDATE wikipoints
            SET
                wp_xindex = ?,
                wp_yindex = ?,
                wp_zindex = ?
            WHERE
                wp_id = ?
            """, "updating indices in wikipoints table", logStart=True), values)

    def selectCoordsAndIds(self):
        return self.select(Query(u"SELECT wp_x, wp_y, wp_id FROM wikipoints"))

    def selectIds(self):
        return self.select(Query(u"SELECT wp_id FROM wikipoints"))

    def selectByTitle(self, title):
        return self.select(Query(u"SELECT * FROM wikipoints WHERE wp_title='{}'".format(title)))

    def selectByIds(self, ids):
        ids = '(' + ','.join(map(str, ids)) + ')'
        return self.select(Query(u"SELECT * FROM wikipoints WHERE wp_id IN {}".format(ids)))

    def selectTitles(self):
        return self.select(Query(u"SELECT wp_title FROM wikipoints"))

class WikimapCategoriesTable(TableProxy):
    def __init__(self, tablePath):
        super(WikimapCategoriesTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query(u"""
            CREATE TABLE wikicategories (
                wc_title        TEXT        NOT NULL,
                wc_page_ids     LIST        NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query(u"INSERT INTO wikicategories VALUES (?,?)", "populating wikicategories table", logStart=True), values)
        self.execute(Query(u"CREATE UNIQUE INDEX title_idx ON wikicategories(wc_title);", "creating index title_idx in wikicategories table", logStart=True, logProgress=True))

    def selectByTitle(self, title):
        return self.select(Query(u"SELECT * FROM wikicategories WHERE wc_title='{}'".format(title)))

    def selectTitles(self):
        return self.select(Query(u"SELECT wc_title FROM wikicategories"))
