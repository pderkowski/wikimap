#!/usr/bin/env python

import os
import sys

class Paths(object):
    def __init__(self, base):
        self.baseDir = os.path.realpath(base)
        self.binDir = self.path(self.baseDir, 'bin')
        self.srcDir = self.path(self.baseDir, 'src')
        self.dataDir = self.path(self.baseDir, 'test')

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


paths = Paths(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
paths.include()


import WikidumpProcessor
import Dictionary
import Link2Vec
import TSNE
import Utils
import time
import logging
import subprocess

class Job(object):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    SKIPPED = 'SKIPPED'
    INTERRUPT = 'INTERRUPT'

    def __init__(self, title, invoke, skipCondition=None):
        self.title = title
        self.invoke = invoke
        self.skipCondition = skipCondition

        self.duration = 0
        self.outcome = 'NONE'

    def run(self):
        t0 = time.time()
        try:
            if self.skipCondition and self.skipCondition():
                self.outcome = Job.SKIPPED
            else:
                self.invoke()
                self.outcome = Job.SUCCESS
        except KeyboardInterrupt:
            self.outcome = Job.INTERRUPT
            raise
        except:
            self.outcome = Job.FAILURE
            raise
        finally:
            self.duration = time.time() - t0

class Jobs(object):
    def __init__(self):
        self.jobs = []

    def add(self, job):
        self.jobs.append(job)

    def run(self):
        logger = logging.getLogger(__name__)

        summary = []
        for job in self.jobs:
            logger.info('STARTING JOB: {}'.format(job.title))

            try:
                job.run()
                summary.append((job.outcome, job.title, job.duration))
            except KeyboardInterrupt:
                summary.append((job.outcome, job.title, job.duration))
                self._printSummary(summary)
                sys.exit(1)
            except Exception, e:
                logger.error(str(e))
                summary.append((job.outcome, job.title, job.duration))

        self._printSummary(summary)


    def _printSummary(self, summary):
        print '-'*80
        print '{:30} |  OUTCOME  |  DURATION   |'.format('JOB SUMMARY')
        print '-'*80

        OKGREEN = '\033[92m'
        OKBLUE = '\033[94m'
        FAILRED = '\033[91m'
        ENDCOLOR = '\033[0m'
        WARNING = '\033[93m'

        for outcome, title, duration in summary:
            if outcome == 'SUCCESS':
                COLOR = OKGREEN
            elif outcome == 'FAILURE':
                COLOR = FAILRED
            elif outcome == 'SKIPPED':
                COLOR = OKBLUE
            else:
                COLOR = WARNING

            print '{:30} | {}[{}]{} | {} |'.format(title, COLOR, outcome, ENDCOLOR, Utils.formatDuration(duration))

        print '-'*80

# DICTIONARY
def buildDictionary():
    WikidumpProcessor.buildDictionary(paths.pageTable, paths.dictionary)

def skipBuildingDictionary():
    return os.path.exists(paths.dictionary)

#LINKS
def buildLinks():
    dictionary = Dictionary.Dictionary()
    dictionary.load(paths.dictionary)
    WikidumpProcessor.buildLinks(paths.linksTable, paths.links, dictionary)

def skipBuildingLinks():
    return os.path.exists(paths.links)

#AGGREGATED LINKS
def buildAggregatedLinks():
    WikidumpProcessor.buildAggregatedLinks(paths.links, paths.aggregatedLinks)

def skipBuildingAggregatedLinks():
    return os.path.exists(paths.aggregatedLinks)

#PAGERANK
def buildPagerank():
    command = ' '.join([paths.pagerankScript, paths.pagerankBin, paths.links, paths.pagerank])
    subprocess.call(command, shell=True)

def skipBuildingPagerank():
    return os.path.exists(paths.pagerank)

#EMBEDDINGS
def buildEmbeddings():
    Link2Vec.build(paths.aggregatedLinks, paths.embeddings)

def skipBuildingEmbeddings():
    return os.path.exists(paths.embeddings)

#TSNE
def buildTSNE():
    TSNE.build(paths.embeddings, paths.tsne)

def skipBuildingTSNE():
    return os.path.exists(paths.tsne)


def main():
    Utils.configLogging()

    jobs = Jobs()
    jobs.add(Job('BUILD DICTIONARY', buildDictionary, skipBuildingDictionary)) #id title
    jobs.add(Job('BUILD LINKS', buildLinks, skipBuildingLinks)) #source target
    jobs.add(Job('BUILD AGGREGATED LINKS', buildAggregatedLinks, skipBuildingAggregatedLinks)) #source list-of-targets-space-separated
    jobs.add(Job('BUILD PAGERANK', buildPagerank, skipBuildingPagerank)) # title pagerank
    jobs.add(Job('BUILD EMBEDDINGS', buildEmbeddings, skipBuildingEmbeddings))
    jobs.add(Job('BUILD TSNE', buildTSNE, skipBuildingTSNE))
    jobs.run()

if __name__ == "__main__":
    main()