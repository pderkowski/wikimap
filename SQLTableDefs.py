from SQLBase import TableProxy, Query

class HighDimensionalNeighborsTable(TableProxy):
    def __init__(self, tablePath):
        super(HighDimensionalNeighborsTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query("""
            CREATE TABLE hdnn (
                hdnn_id                 INTEGER     NOT NULL    PRIMARY KEY,
                hdnn_neighbors_ids      LIST        NOT NULL,
                hdnn_neighbors_dists    LIST        NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO hdnn VALUES (?,?,?)", "populating hdnn table", logStart=True), values)

class LowDimensionalNeighborsTable(TableProxy):
    def __init__(self, tablePath):
        super(LowDimensionalNeighborsTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query("""
            CREATE TABLE ldnn (
                ldnn_id                 INTEGER     NOT NULL    PRIMARY KEY,
                ldnn_neighbors_ids      LIST        NOT NULL,
                ldnn_neighbors_dists    LIST        NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO ldnn VALUES (?,?,?)", "populating ldnn table", logStart=True), values)

class WikimapPointsTable(TableProxy):
    def __init__(self, tablePath):
        super(WikimapPointsTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query("""
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
        self.executemany(Query("""
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

        self.execute(Query("CREATE UNIQUE INDEX title_idx ON wikipoints(wp_title);", "creating index title_idx in wikipoints table", logStart=True, logProgress=True))

    def updateIndices(self, values):
        self.executemany(Query("""
            UPDATE wikipoints
            SET
                wp_xindex = ?,
                wp_yindex = ?,
                wp_zindex = ?
            WHERE
                wp_id = ?
            """, "updating indices in wikipoints table", logStart=True), values)

    def selectCoordsAndIds(self):
        return self.select(Query("SELECT wp_x, wp_y, wp_id FROM wikipoints"))

    def selectIds(self):
        return self.select(Query("SELECT wp_id FROM wikipoints"))

    def selectByTitle(self, title):
        return self.select(Query("SELECT * FROM wikipoints WHERE wp_title={}".format(title)))

    def selectByIds(self, ids):
        return self.select(Query("SELECT * FROM wikipoints WHERE wp_id IN {}".format(tuple(ids))))

class WikimapCategoriesTable(TableProxy):
    def __init__(self, tablePath):
        super(WikimapCategoriesTable, self).__init__(tablePath, useCustomTypes=True)

    def create(self):
        self.execute(Query("""
            CREATE TABLE wikicategories (
                wc_title        TEXT        NOT NULL,
                wc_page_ids     LIST        NOT NULL
            );"""))

    def populate(self, values):
        self.executemany(Query("INSERT INTO wikicategories VALUES (?,?)", "populating wikicategories table", logStart=True), values)
