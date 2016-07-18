#!/usr/bin/env python

import WikidumpProcessor
import Dictionary
import Link2Vec
import TSNE
import Utils
import Paths
import time
import logging
import subprocess
import os

paths = Paths.Paths(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
paths.include()

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