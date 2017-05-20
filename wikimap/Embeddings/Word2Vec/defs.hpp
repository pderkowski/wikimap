#pragma once

#include <cstdint>
#include <vector>
#include <utility>
#include <unordered_map>


namespace w2v {


typedef float Float;
typedef std::vector<Float> Embedding;

template<class Word>
using Embeddings = std::unordered_map<Word, Embedding>;

typedef int64_t Int;
typedef int32_t Id;
typedef std::vector<Id> Sequence;
typedef typename Sequence::const_iterator SequenceIterator;
typedef std::pair<SequenceIterator, SequenceIterator> SequenceRange;


// defaults defined here for consistency
namespace def {

const int DIMENSION = 100;
const int EPOCHS = 1;
const double LEARNING_RATE = 0.025;
const int CONTEXT_SIZE = 5;
const bool DYNAMIC_CONTEXT = true;
const int NEGATIVE_SAMPLES = 5;
const bool VERBOSE = true;
const double SUMBSAMPLING_FACTOR = 0.75;
const bool BINARY = false;

}


}
