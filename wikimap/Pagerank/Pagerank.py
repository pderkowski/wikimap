from subprocess import PIPE, Popen
import os

def pagerank(input, verbosity=1):
    directory = os.path.dirname(os.path.realpath(__file__))
    pagerankPath = os.path.join(directory, 'pagerank')

    process = Popen([pagerankPath, str(verbosity)], stdin=PIPE, stdout=PIPE)

    with process.stdin:
        for line in input:
            process.stdin.write(line)

    for line in process.stdout:
        line = line.rstrip()
        if line:
            id, rank = line.split()
            yield (id, rank)

    process.wait()
