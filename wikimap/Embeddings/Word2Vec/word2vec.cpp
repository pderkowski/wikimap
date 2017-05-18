#include <cstdio>

#include "io.hpp"
#include "word2vec.hpp"

const char* help_message = R"(
word2vec

Options:
    -h, -help, --help
        Print this message and exit.
    -i, -input <file>
        Use data from <file> to train the model. [Default: stdin]
    -o, -output <file>
        Save word vectors to <file>. [Default: stdout]
    -s, -size <int>
        Set size of word vectors. [Default: 100]
    -e, -epochs <int>
        Set number of passes over data for training. [Default: 1]
    -w, -window <int>
        Set max skip length between words. [Default: 5]
    -n, -negative <int>
        Number of negative examples. Common values are 5-10. [Default: 5]
    -a, -alpha <float>
        Set the starting learning rate. [Default: 0.025]
    -d, -dynamic <int>
        Use sampling to determine actual window for each word. [Default: 1 (on)]
    -b, -binary <int>
        Save the resulting vectors in binary mode. [Default: 0 (off)]
    -v, -verbose <int>
        Enable info prints. [Default: 1 (on)]

Examples:
    ./word2vec -input data.txt -output vec.txt -size 200 -window 5 -negative 5 -binary 0

)";

int main(int argc, const char* argv[]) {
    auto args = w2v::Args(argc, argv);

    if (argc == 1 || args.has({"-h", "-help", "--help"})) {
        fprintf(stderr, "%s", help_message);
        return 0;
    }

    auto input  = args.get({"-i", "-input", "-train"}, "stdin");
    auto output = args.get({"-o", "-output"}, "stdout");
    auto size = args.get({"-s", "-size"}, 100);
    auto epochs = args.get({"-e", "-epochs"}, 1);
    auto window = args.get({"-w", "-window"}, 5);
    auto negative = args.get({"-n", "-negative"}, 5);
    auto alpha = args.get({"-a", "-alpha"}, 0.025);
    auto dynamic = args.get({"-d", "-dynamic"}, 1);
    auto binary = args.get({"-b", "-binary"}, 0);
    auto verbose = args.get({"-v", "-verbose"}, 1);

    auto word2vec = w2v::Word2Vec<>(size, epochs, alpha, window, dynamic,
        negative, verbose);

    auto text_input = w2v::read(input, verbose);
    auto embeddings = word2vec.learn_embeddings(text_input);
    w2v::write(embeddings, output, binary, verbose);

    return 0;
}