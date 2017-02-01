from subprocess import Popen, PIPE
import os
import tempfile
import logging
import sys

def Node2Vec(edges, dims=128, walkLength=80, walksPerNode=10, contextSize=10, epochsCount=1, returnParam=1, inoutParam=1, verbose=True, directed=True, weighted=False):
    logger = logging.getLogger(__name__)
    directory = os.path.dirname(os.path.realpath(__file__))
    binPath = os.path.join(directory, "node2vec")

    tmpOutput = tempfile.NamedTemporaryFile()

    args = [binPath,
        "-o:{}".format(tmpOutput.name),
        "-d:{}".format(str(dims)),
        "-l:{}".format(str(walkLength)),
        "-r:{}".format(str(walksPerNode)),
        "-k:{}".format(str(contextSize)),
        "-e:{}".format(str(epochsCount)),
        "-p:{}".format(str(returnParam)),
        "-q:{}".format(str(inoutParam))]
    if verbose:
        args.append("-v")
    if directed:
        args.append("-dr")
    if weighted:
        args.append("-w")

    process = Popen(args, stdin=PIPE, stdout=sys.stdout, stderr=sys.stderr, bufsize=-1)

    logger.info("Running node2vec...")
    with process.stdin:
        for (start, end) in edges:
            process.stdin.write(str(start) + ' ' + str(end) + '\n')

    process.wait()

    logger.info("")
    next(tmpOutput) # skip the first line
    for line in tmpOutput:
        line = line.rstrip()
        if line:
            words = line.split()
            embedding = map(float, words[1:])
            if len(embedding) != dims:
                sys.stdout.write(line)
                raise Exception('Invalid embedding length')
            yield (int(words[0]), embedding)
