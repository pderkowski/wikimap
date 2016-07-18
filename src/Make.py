#!/usr/bin/env python

from Job import Jobs, Job
from Paths import Paths
import Utils
import os
import urllib

paths = Paths(Utils.getParentDirectory(__file__))
paths.include()

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

def main():
    Utils.configLogging()

    jobs = Jobs()
    jobs.add(Job('CREATE DIRECTORIES', createDirs, skipCreatingDirs))
    jobs.add(Job('DOWNLOAD DATA', downloadData, skipDownloadingData))
    jobs.run()

if __name__ == "__main__":
    main()