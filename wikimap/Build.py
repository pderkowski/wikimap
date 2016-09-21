import Link2Vec
import TSNE
from Job import Job
import Utils
import subprocess
import os
import DataProcessor
import urllib
import Pagerank

def download(url):
    return lambda output: urllib.urlretrieve(url, output, reporthook=Utils.ProgressBar(url).report)

def build():
    pageUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
    linksUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'
    categoryUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-category.sql.gz'
    categoryLinksUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-categorylinks.sql.gz'
    pageSql = 'page.sql.gz'
    linksSql = 'pagelinks.sql.gz'
    categorySql = 'category.sql.gz'
    categoryLinksSql = 'categorylinks.sql.gz'
    page = 'page.db'
    links = 'links.db'
    category = 'category.db'
    categoryLinks = 'categoryLinks.db'
    normalizedLinks = 'normalizedLinks.db'
    pagerank = 'pagerank.db'
    embeddings = 'embeddings'
    embeddingsArtifacts = [embeddings+a for a in ['.syn0_lockf.npy', '.syn0.npy', '.syn1neg.npy']]
    tsne = 'tsne.db'
    final = 'final'

    jobs = []
    jobs.append(Job('DOWNLOAD PAGE TABLE', download(pageUrl), inputs = [], outputs = [pageSql]))
    jobs.append(Job('DOWNLOAD LINKS TABLE', download(linksUrl), inputs = [], outputs = [linksSql]))
    jobs.append(Job('DOWNLOAD CATEGORY TABLE', download(categoryUrl), inputs = [], outputs = [categorySql]))
    jobs.append(Job('DOWNLOAD CATEGORY LINKS TABLE', download(categoryLinksUrl), inputs = [], outputs = [categoryLinksSql]))
    jobs.append(Job('LOAD PAGE TABLE', DataProcessor.loadPageTable, inputs = [pageSql], outputs = [page]))
    jobs.append(Job('LOAD LINKS TABLE', DataProcessor.loadLinksTable, inputs = [linksSql], outputs = [links]))
    jobs.append(Job('LOAD CATEGORY TABLE', DataProcessor.loadCategoryTable, inputs = [categorySql], outputs = [category]))
    jobs.append(Job('LOAD CATEGORY LINKS TABLE', DataProcessor.loadCategoryLinksTable, inputs = [categoryLinksSql], outputs = [categoryLinks]))
    jobs.append(Job('NORMALIZE LINKS', DataProcessor.normalizeLinks, inputs = [page, links], outputs = [normalizedLinks]))
    jobs.append(Job('COMPUTE PAGERANK', DataProcessor.computePagerank, inputs = [normalizedLinks], outputs = [pagerank]))
    jobs.append(Job('COMPUTE EMBEDDINGS', DataProcessor.computeEmbeddings, inputs = [normalizedLinks], outputs = [embeddings], artifacts = embeddingsArtifacts))
    jobs.append(Job('COMPUTE TSNE', DataProcessor.computeTSNE, inputs = [embeddings, pagerank], outputs = [tsne]))
    jobs.append(Job('COMPUTE FINAL TABLE', DataProcessor.computeFinalTable, inputs = [tsne, page], outputs = [final]))

    return jobs
