import WikidumpProcessor
import Link2Vec
import TSNE
from Job import Job
import Utils
import subprocess
import os
import DataProcessor
import urllib
import Pagerank
import SqliteWrapper

def download(url):
    return lambda output: urllib.urlretrieve(url, output, reporthook=Utils.ProgressBar(url).report)

def build():
    pageTableUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
    linksTableUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'
    pageTableSql = 'page.sql.gz'
    linksTableSql = 'pagelinks.sql.gz'
    pages = 'page.db'
    links = 'links.db'
    normalizedLinks = 'normalizedLinks.db'
    pagerank = 'pagerank.db'
    embeddings = 'embeddings'
    embeddingsArtifacts = [embeddings+a for a in ['.syn0_lockf.npy', '.syn0.npy', '.syn1neg.npy']]
    tsne = 'tsne.db'
    final = 'final'

    jobs = []
    jobs.append(Job('DOWNLOAD PAGE TABLE', download(pageTableUrl), inputs = [], outputs = [pageTableSql]))
    jobs.append(Job('DOWNLOAD LINKS TABLE', download(linksTableUrl), inputs = [], outputs = [linksTableSql]))
    jobs.append(Job('LOAD PAGE TABLE', SqliteWrapper.pages.loadTable, inputs = [pageTableSql], outputs = [pages]))
    jobs.append(Job('LOAD LINKS TABLE', SqliteWrapper.links.loadTable, inputs = [linksTableSql], outputs = [links]))
    jobs.append(Job('NORMALIZE LINKS', DataProcessor.normalizeLinks, inputs = [pages, links], outputs = [normalizedLinks]))
    jobs.append(Job('COMPUTE PAGERANK', DataProcessor.computePagerank, inputs = [normalizedLinks], outputs = [pagerank]))
    jobs.append(Job('COMPUTE EMBEDDINGS', DataProcessor.computeEmbeddings, inputs = [normalizedLinks], outputs = [embeddings], artifacts = embeddingsArtifacts))
    jobs.append(Job('COMPUTE TSNE', DataProcessor.computeTSNE, inputs = [embeddings, pagerank], outputs = [tsne]))
    jobs.append(Job('COMPUTE FINAL TABLE', DataProcessor.computeFinalTable, inputs = [tsne, pages], outputs = [final]))

    return jobs
