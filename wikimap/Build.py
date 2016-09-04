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

def download(url):
    return lambda output: urllib.urlretrieve(url, output, reporthook=Utils.ProgressBar(url).report)

def build():
    pageTableUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-page.sql.gz'
    linksTableUrl = 'https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pagelinks.sql.gz'
    pageTable = 'page.sql.gz'
    linksTable = 'pagelinks.sql.gz'
    dictionary = 'dictionary'
    links = 'links'
    aggregatedLinks = 'aggregatedLinks'
    pagerank = 'pagerank'
    embeddings = 'embeddings'
    tsne = 'tsne'
    final = 'final'

    jobs = []
    jobs.append(Job('DOWNLOAD PAGETABLE', download(pageTableUrl), inputs = [], outputs = [pageTable]))
    jobs.append(Job('DOWNLOAD LINKSTABLE', download(linksTableUrl), inputs = [], outputs = [linksTable]))
    jobs.append(Job('BUILD DICTIONARY', WikidumpProcessor.buildDictionary, inputs = [pageTable], outputs = [dictionary])) #id title
    jobs.append(Job('BUILD LINKS', WikidumpProcessor.buildLinks, inputs = [dictionary, linksTable], outputs = [links])) #source target
    jobs.append(Job('BUILD AGGREGATED LINKS', WikidumpProcessor.buildAggregatedLinks, inputs = [links], outputs = [aggregatedLinks])) #source list-of-targets-space-separated
    jobs.append(Job('BUILD PAGERANK', Pagerank.pagerank, inputs = [links], outputs = [pagerank])) # title pagerank
    jobs.append(Job('BUILD EMBEDDINGS', Link2Vec.build, inputs = [aggregatedLinks], outputs = [embeddings]))
    jobs.append(Job('BUILD TSNE', TSNE.run, inputs = [embeddings, pagerank], outputs = [tsne]))
    jobs.append(Job('BUILD FINAL', DataProcessor.buildFinalTable, inputs = [tsne, dictionary], outputs = [final]))

    return jobs
