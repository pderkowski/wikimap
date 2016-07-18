import os
import sys

class Paths(object):
    def __init__(self, base):
        self.baseDir = os.path.realpath(base)
        self.binDir = self.path(self.baseDir, 'bin')
        self.srcDir = self.path(self.baseDir, 'src')

        if 'DATAPATH' in os.environ:
            self.dataDir = os.environ['DATAPATH']
        else:
            self.dataDir = self.path(self.baseDir, 'data')

        self.pageTableUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
        self.linksTableUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'

        self.pageTable = self.path(self.dataDir, 'enwiki-latest-page.sql')
        self.linksTable = self.path(self.dataDir, 'enwiki-latest-pagelinks.sql')

        self.dictionary = self.path(self.dataDir, 'dictionary')
        self.links = self.path(self.dataDir, 'links')
        self.aggregatedLinks = self.path(self.dataDir, 'aggregatedLinks')
        self.pagerank = self.path(self.dataDir, 'pagerank')
        self.embeddings = self.path(self.dataDir, 'embeddings')
        self.tsne = self.path(self.dataDir, 'tsne')

        self.pagerankBin = self.path(self.binDir, 'pagerank')
        self.pagerankScript = self.path(self.srcDir, 'Pagerank.sh')

    def path(self, path, *paths):
        return os.path.realpath(os.path.join(path, *paths))

    def include(self):
        sys.path.insert(1, self.srcDir)