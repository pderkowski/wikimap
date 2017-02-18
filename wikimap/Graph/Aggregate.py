from subprocess import PIPE, Popen
import os

def aggregate(nodes, edges, depth=1):
    directory = os.path.dirname(os.path.realpath(__file__))
    aggregatePath = os.path.join(directory, 'aggregate')

    process = Popen([aggregatePath, str(depth)], stdin=PIPE, stdout=PIPE, bufsize=100000)

    with process.stdin:
        for (what, at) in nodes:
            line = u'd ' + at + u' ' + str(what) + u'\n'
            process.stdin.write(line.encode('utf8'))

        for (what, at) in edges:
            line = u'e ' + at + u' ' + what + u'\n'
            process.stdin.write(line.encode('utf8'))

    for line in process.stdout:
        line = line.decode('utf8')
        line = line.rstrip()
        words = line.split()
        if line:
            yield (words[0], map(int, words[1:]))

    process.wait()
