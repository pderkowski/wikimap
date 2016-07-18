import mmap
import re
import logging
import os
import sys
import tempfile
import subprocess
import itertools
import Dictionary
import Utils

num = r'[0-9]+'
delimitedWord = r"'(?:\\.|[^\\']+)'" # (?: ) --> match either; \\. --> any special char; | --> or; [^\\']++ --> not \ and ';
whatever = r"[^)]+"

def processSqlDump(input, output, startPattern, matchPattern, acceptFun, formatFun):
    logger = logging.getLogger(__name__)

    with Utils.openOrExit(input,'r') as input, Utils.openOrExit(output,'w') as output:
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


def buildDictionary(input, output):
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


def buildLinks(input, output, dictionary):
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

    processSqlDump(input, output, startPattern, matchPattern, acceptFun, formatFun) # make a list of <idFrom, idTo> newline separated, write to tmpOutput
    command = 'sort -n -o {} {}'.format(output, output)
    logger.info('Running sort: {}'.format(command))
    subprocess.call(command.split()) # sort this list

def buildAggregatedLinks(input, output):
    input = Utils.openOrExit(input,'r')
    output = Utils.openOrExit(output,'w')

    for k, group in itertools.groupby(input, lambda line: line.split()[0]):
        output.write(' '.join([k] + [val.rstrip().split()[1] for val in group])+'\n')

    output.close()
    input.close()

