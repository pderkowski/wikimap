from subprocess import Popen, PIPE
import logging
import sys
import os
import tempfile


def _find_executable(exec_name):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    exec_path = os.path.join(current_dir, exec_name)
    if os.path.exists(exec_path):
        return exec_path
    else:
        raise IOError('File not found.')


def _iterate_embeddings(file_, expected_dimensions):
    next(file_)  # skip the first line
    for line in file_:
        line = line.strip()
        if line:
            words = line.split()
            embedding = map(float, words[1:])
            if len(embedding) != expected_dimensions:
                sys.stdout.write(line)
                raise Exception('Invalid embedding length')
            yield (int(words[0]), embedding)


def Word2Vec(sentences, dimensions, context_size, epochs_count, dynamic_window,
             verbose):
    """Run word2vec on provided sentences."""
    logger = logging.getLogger(__name__)

    exec_path = _find_executable('word2vec')
    temp_output = tempfile.NamedTemporaryFile()

    args = [
        exec_path,
        '-o', temp_output.name,
        '-s', str(dimensions),
        '-w', str(context_size),
        '-e', str(epochs_count)
    ]

    if verbose:
        args.extend(['-v', '1'])
    if not dynamic_window:
        args.extend(['-d', '0'])

    process = Popen(args, stdin=PIPE, stdout=sys.stdout, stderr=sys.stderr,
                    bufsize=-1)

    logger.info("Running word2vec...")
    with process.stdin:
        for sentence in sentences:
            process.stdin.write(' '.join(map(str, sentence)) + '\n')

    process.wait()
    logger.info("")
    return iter(_iterate_embeddings(temp_output, dimensions))
