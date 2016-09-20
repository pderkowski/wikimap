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
    pageTable = 'page.db'
    linksTable = 'links.db'
    dictionary = 'dictionary'
    normalizedLinks = 'normalizedLinks.db'
    aggregatedLinks = 'aggregatedLinks'
    pagerank = 'pagerank.db'
    embeddings = 'embeddings'
    tsne = 'tsne'
    final = 'final'

    jobs = []
    jobs.append(Job('DOWNLOAD PAGE TABLE', download(pageTableUrl), inputs = [], outputs = [pageTableSql]))
    jobs.append(Job('DOWNLOAD LINKS TABLE', download(linksTableUrl), inputs = [], outputs = [linksTableSql]))
    jobs.append(Job('LOAD PAGE TABLE', SqliteWrapper.pageTable.loadTable, inputs = [pageTableSql], outputs = [pageTable]))
    jobs.append(Job('LOAD LINKS TABLE', SqliteWrapper.linksTable.loadTable, inputs = [linksTableSql], outputs = [linksTable]))
    jobs.append(Job('NORMALIZE LINKS', DataProcessor.normalizeLinks, inputs = [pageTable, linksTable], outputs = [normalizedLinks]))
    jobs.append(Job('COMPUTE PAGERANK', DataProcessor.computePagerank, inputs = [normalizedLinks], outputs = [pagerank]))

    # jobs.append(Job('BUILD EMBEDDINGS', Link2Vec.build, inputs = [aggregatedLinks], outputs = [embeddings]))
    # jobs.append(Job('BUILD TSNE', TSNE.run, inputs = [embeddings, pagerank], outputs = [tsne]))
    # jobs.append(Job('BUILD FINAL', DataProcessor.buildFinalTable, inputs = [tsne, dictionary], outputs = [final]))

    # jobs.append(Job('BUILD DICTIONARY', WikidumpProcessor.buildDictionary, inputs = [pageTable], outputs = [dictionary])) #id title
    # jobs.append(Job('BUILD LINKS', WikidumpProcessor.buildLinks, inputs = [dictionary, linksTable], outputs = [links])) #source target
    # jobs.append(Job('BUILD AGGREGATED LINKS', WikidumpProcessor.buildAggregatedLinks, inputs = [links], outputs = [aggregatedLinks])) #source list-of-targets-space-separated

    return jobs
