#!/usr/bin/env python

import mmap
import re
import logging
import os
import sys
import argparse
import tempfile
import subprocess
import itertools
import Dictionary
import Utils


dataPath = '../data'

pageTablePath = os.path.join(dataPath, 'enwiki-latest-page.sql')
linksTablePath = os.path.join(dataPath, 'enwiki-latest-pagelinks.sql')

dictionaryPath = os.path.join(dataPath, 'dictionary')
linksPath = os.path.join(dataPath, 'links')

num = r'[0-9]+'
delimitedWord = r"'(?:\\.|[^\\']+)'" # (?: ) --> match either; \\. --> any special char; | --> or; [^\\']++ --> not \ and ';
whatever = r"[^)]+"


class Stats(object):
    def __init__(self):
        self.dictConstrTime = Utils.Timer('Dictionary construction')
        self.dictLoadTime = Utils.Timer(name='Dictionary load')
        self.linkTotalConstrTime = Utils.Timer(name='Total link construction')

    def log(self):
        logger = logging.getLogger(__name__)

        logger.info(str(self.dictConstrTime))
        logger.info(str(self.dictLoadTime))
        logger.info(str(self.linkTotalConstrTime))


def processSqlDump(input, output, startPattern, matchPattern, acceptFun, formatFun):
    logger = logging.getLogger(__name__)

    input = Utils.openOrExit(input,'r')
    output = Utils.openOrExit(output,'w')
    mm = mmap.mmap(input.fileno(), 0, prot=mmap.PROT_READ)

    reMatch = re.compile(matchPattern)

    # move the file position to the beginning of the relevant data
    mm.seek(mm.find(startPattern) + len(startPattern) + 1) # + 1 space

    written = 0
    total = 0

    for i, match in enumerate(re.finditer(reMatch, mm)):
        if i % 1000000 == 0:
            logger.info('Processed {} records.'.format(i, written))

        total += 1

        if acceptFun(match):
            output.write(formatFun(match))
            written += 1

    logger.info('Processed {} records, {} of them matched the pattern.'.format(total, written))

    mm.close()
    output.close()
    input.close()


def constructDictionary(input, output):
    logger = logging.getLogger(__name__)

    startPattern = 'INSERT INTO `page` VALUES'
    matchPattern = '\(({}),({}),({}),{}\)'.format(num, num, delimitedWord, whatever)

    def acceptFun(match):
        ns = int(match.group(2))
        return ns == 0

    def formatFun(match):
        id = match.group(1)
        title = match.group(3).decode('string-escape')
        return '{} {}\n'.format(id, title)

    processSqlDump(input, output, startPattern, matchPattern, acceptFun, formatFun)


def constructLinks(input, output, dictionary):
    logger = logging.getLogger(__name__)

    startPattern = 'INSERT INTO `pagelinks` VALUES'
    matchPattern = '\(({}),({}),({}),({})\)'.format(num, num, delimitedWord, num)

    def acceptFun(match):
        idFrom = int(match.group(1))
        ns1 = int(match.group(2))
        ns2 = int(match.group(4))
        title = match.group(3).decode('string-escape')

        return idFrom in dictionary.id2title and ns1 == 0 and ns2 == 0 and title in dictionary.title2id

    def formatFun(match):
        idFrom = match.group(1)
        title = match.group(3).decode('string-escape')
        idTo = dictionary.title2id[title]
        return '{} {}\n'.format(idFrom, idTo)

    try:
        tmpOutput = tempfile.NamedTemporaryFile(delete=False)
        processSqlDump(input, tmpOutput.name, startPattern, matchPattern, acceptFun, formatFun) # make a list of <idFrom, idTo> newline separated, write to tmpOutput
        logger.info('Started sorting links.')
        command = 'sort -n -o {} {}'.format(tmpOutput.name, tmpOutput.name)
        logger.info('Running sort: {}'.format(command))
        subprocess.call(command.split()) # sort this list
        logger.info('Finished sorting links.')
        logger.info('Started aggregating links.')
        aggregateLinks(tmpOutput.name, output) # aggregate the links to lists
        logger.info('Finished aggregating links.')
    except KeyboardInterrupt:
        logger.info('Interrupted, cleaning up.')
    finally:
        os.unlink(tmpOutput.name)

def aggregateLinks(input, output):
    logger = logging.getLogger(__name__)

    input = Utils.openOrExit(input,'r')
    output = Utils.openOrExit(output,'w')

    for k, group in itertools.groupby(input, lambda line: line.split()[0]):
        output.write(' '.join([k] + [val.rstrip().split()[1] for val in group])+'\n')

    output.close()
    input.close()

def processWikidump(rebuild=False):
    logger = logging.getLogger(__name__)
    stats = Stats()

    # STEP 1: Construct the dictionary
    logger.info('CONSTRUCTING DICTIONARY ID <---> TITLE.')

    stats.dictConstrTime.start()

    if not os.path.exists(dictionaryPath):
        logger.info('Dictionary not found, starting construction.')
        constructDictionary(pageTablePath, dictionaryPath)
    elif rebuild:
        logger.info('Rebuild flag is on, starting construction.')
        constructDictionary(pageTablePath, dictionaryPath)
    else:
        logger.info('Dictionary found, skipping construction.')

    stats.dictConstrTime.stop()

    # STEP 2: Load the dictionary from disk
    logger.info('LOADING DICTIONARY FROM DISK')

    stats.dictLoadTime.start()
    dictionary = Dictionary.Dictionary()
    dictionary.load(dictionaryPath)
    stats.dictLoadTime.stop()

    logger.info('Dictionary has {} records.'.format(len(dictionary.id2title)))

    #STEP 3: Construct the list of links
    logger.info('CONSTRUCTING LINKS')

    stats.linkTotalConstrTime.start()
    if not os.path.exists(linksPath):
        logger.info('Links not found, starting construction.')
        constructLinks(linksTablePath, linksPath, dictionary)
    elif rebuild:
        logger.info('Rebuild flag is on, starting construction.')
        constructLinks(linksTablePath, linksPath, dictionary)
    else:
        logger.info('Links found, skipping construction.')

    stats.linkTotalConstrTime.stop()

    stats.log()

def main():
    Utils.configLogging()

    parser = argparse.ArgumentParser(description='Process Wikidump files to obtain a list of all the links.')
    parser.add_argument('--rebuild', '-r', action='store_true', default=False, help='Do not use files from previous runs if any are present.')

    args = parser.parse_args()

    processWikidump(rebuild=args.rebuild)

if __name__ == '__main__':
    main()