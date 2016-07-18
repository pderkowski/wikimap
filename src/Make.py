#!/usr/bin/env python

from Job import Jobs, Job
from Paths import Paths
import Utils
import os

paths = Paths(Utils.getParentDirectory(__file__))
paths.include()

# DIRS
def createDirs():
    for d in [paths.binDir, paths.libDir, paths.dataDir]:
        if not os.path.exists(d):
            os.makedirs(d)

def skipCreatingDirs():
    return all(os.path.exists(d) for d in [paths.binDir, paths.libDir, paths.dataDir])

def main():
    Utils.configLogging()

    jobs = Jobs()
    jobs.add(Job('CREATE DIRECTORIES', createDirs, skipCreatingDirs))
    jobs.run()

if __name__ == "__main__":
    main()