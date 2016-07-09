#!/usr/bin/env python

import tempfile
import os
import Utils
import logging
import subprocess

dataPath = '../data'
binPath = '../bin'
linksPath = os.path.join(dataPath, 'links')
linksExpandedPath = os.path.join(dataPath, 'links_expanded')

pagerankBinPath = os.path.join(binPath, 'pagerank')
pagerankPath = os.path.join(dataPath, 'pagerank')

def expandLines(linksPath, outputPath):
    logger  = logging.getLogger(__name__)

    with open(linksPath,'r') as links, open(outputPath,'w') as output:
        for i, line in enumerate(links):
            if i % 1000000 == 0:
                logger.info('Expanded {} lines.'.format(i))
            parts = line.rstrip().split()
            origin = parts[0]
            targets = parts[1:]

            for t in targets:
                output.write('{} {}\n'.format(origin, t))

def main():
    Utils.configLogging()
    logger = logging.getLogger(__name__)

    logger.info('CONSTRUCTING PAGERANK FOR LINKS.')

    if os.path.exists(linksExpandedPath):
        logger.info('Found expanded links, skipping construction.')
    else:
        logger.info('Starting expanding links.')
        expandLines(linksPath, linksExpandedPath)
        logger.info('Finished expanding links')

    if os.path.exists(pagerankPath):
        logger.info('Found pagerank, skipping construction.')
    else:
        args = [pagerankBinPath, '-o', pagerankPath, linksExpandedPath]
        logger.info('Starting calculating pagerank: {}'.format(args))
        subprocess.call(args)
        logger.info('Finished calculating pagerank.')

if __name__=="__main__":
    main()