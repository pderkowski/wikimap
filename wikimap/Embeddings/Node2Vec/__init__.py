from subprocess import Popen, PIPE
import os
import tempfile
import logging
import sys


def Node2Vec(edges, dimensions, context_size, backtrack_prob, walks_per_node,
             walk_length=80, epochs_count=1, verbose=True):
    logger = logging.getLogger(__name__)
    directory = os.path.dirname(os.path.realpath(__file__))
    binPath = os.path.join(directory, "node2vec")

    tmpOutput = tempfile.NamedTemporaryFile()

    args = [binPath,
        "-o:{}".format(tmpOutput.name),
        "-d:{}".format(str(dimensions)),
        "-l:{}".format(str(walk_length)),
        "-r:{}".format(str(walks_per_node)),
        "-k:{}".format(str(context_size)),
        "-e:{}".format(str(epochs_count)),
        "-b:{}".format(str(backtrack_prob))]
    if verbose:
        args.append("-v")

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
            if len(embedding) != dimensions:
                sys.stdout.write(line)
                raise Exception('Invalid embedding length')
            yield (int(words[0]), embedding)
