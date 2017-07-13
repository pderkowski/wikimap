#include <cstdio>

#include "io.hpp"
#include "word2vec.hpp"
#include "corpus.hpp"

const char* help_message = R"(
word2vec

Options:
    -h, -help, --help
        Print this message and exit.
    -i, -input, -train <file>
        Use data from <file> to train the model. REQUIRED.
    -o, -output <file>
        Save word vectors to <file>. REQUIRED.
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
    -v, -verbose <int>
        Enable info prints. [Default: 1 (on)]

Examples:
    ./word2vec -input data.txt -output vec.txt -size 200 -window 5 -negative 5 -binary 0

)";

int main(int argc, const char* argv[]) {
    auto args = emb::Args(argc, argv);

    if (argc == 1 || args.has({"-h", "-help", "--help"})) {
        fprintf(stderr, "%s", help_message);
        return 1;
    }

    if (!args.has({ "-i", "-input", "-train" })) {
        fprintf(stderr, "%s", "Missing input argument.\n");
        return 1;
    }

    if (!args.has({ "-o", "-output" })) {
        fprintf(stderr, "%s", "Missing output argument.\n");
        return 1;
    }

    auto input = args.get_string({"-i", "-input", "-train"});
    auto output = args.get_string({"-o", "-output"});
    auto size = args.get_int({"-s", "-size"}, emb::def::DIMENSION);
    auto epochs = args.get_int({"-e", "-epochs"}, emb::def::EPOCHS);
    auto window = args.get_int({"-w", "-window"}, emb::def::CONTEXT_SIZE);
    auto negative = args.get_int(
        {"-n", "-negative"},
        emb::def::NEGATIVE_SAMPLES);
    auto alpha = args.get_float({"-a", "-alpha"}, emb::def::LEARNING_RATE);
    auto dynamic = args.get_int({"-d", "-dynamic"}, emb::def::DYNAMIC_CONTEXT);
    auto verbose = args.get_int({"-v", "-verbose"}, emb::def::VERBOSE);

    auto w2v = emb::Word2Vec<>(size, epochs, alpha, window, dynamic,
        negative, verbose);

    auto text = emb::read(input, verbose);
    emb::MemoryCorpus<decltype(w2v)::value_type> corpus(
        text.begin(),
        text.end());
    w2v.train(corpus);
    auto embeddings = w2v.get_embeddings();
    embeddings.save(output);
    return 0;
}