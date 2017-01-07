from subprocess import PIPE, Popen
import os

def pagerank(input, verbosity=1):
    directory = os.path.dirname(os.path.realpath(__file__))
    pagerankPath = os.path.join(directory, 'pagerank')

    process = Popen([pagerankPath, str(verbosity)], stdin=PIPE, stdout=PIPE, bufsize=-1)

    with process.stdin:
        for (start, end) in input:
            process.stdin.write(str(start) + ' ' + str(end) + '\n')

    for line in process.stdout:
        line = line.rstrip()
        if line:
            yield tuple(line.split())

    process.wait()
