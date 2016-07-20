#!/usr/bin/env python

from Job import Jobs, Job
from Paths import Paths
import Utils
import os
import urllib
import logging

paths = Paths(Utils.getParentDirectory(__file__))
paths.include()

def dependencyChanged(file, dependencies):
    return any(os.path.getctime(dep) > os.path.getctime(file) for dep in dependencies)

# DIRS
def createDirs():
    for d in [paths.binDir, paths.dataDir]:
        if not os.path.exists(d):
            os.makedirs(d)

def skipCreatingDirs():
    return all(os.path.exists(d) for d in [paths.binDir, paths.dataDir])

# DATA
def downloadData():
    urllib.urlretrieve(paths.pageTableUrl, paths.pageTable, reporthook=Utils.ProgressBar(paths.pageTableUrl).report)
    urllib.urlretrieve(paths.linksTableUrl, paths.linksTable, reporthook=Utils.ProgressBar(paths.linksTableUrl).report)

def skipDownloadingData():
    return all(os.path.exists(d) for d in [paths.pageTable, paths.linksTable])

# COMPILATION
def compileSources():
    if not skipCompilation(paths.bhtsneBin, paths.bhtsneSources):
        compileBHTSNE = "g++ -o {} {} -O2".format(paths.bhtsneBin, ' '.join(paths.bhtsneSources))
        Utils.call(compileBHTSNE)

    if not skipCompilation(paths.pagerankBin, paths.pagerankSources):
        compilePagerank = "g++ -std=c++11 -o {} {} -O2".format(paths.pagerankBin, ' '.join(paths.pagerankSources))
        Utils.call(compilePagerank)

def skipCompilation(binary, sources):
    return os.path.exists(binary) and not dependencyChanged(binary, sources)

def main():
    Utils.configLogging()

    jobs = Jobs()
    jobs.add(Job('CREATE DIRECTORIES', createDirs, skipCreatingDirs))
    jobs.add(Job('DOWNLOAD DATA', downloadData, skipDownloadingData))
    jobs.add(Job('COMPILE SOURCES', compileSources))
    jobs.run()

if __name__ == "__main__":
    main()