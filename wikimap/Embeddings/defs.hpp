#pragma once

#include <cstdint>
#include <vector>
#include <utility>
#include <unordered_map>


namespace emb {


typedef float Float;
typedef std::vector<Float> Embedding;

template<class Word>
using Sentence = std::vector<Word>;

template<class Word>
using SentenceIterator = typename Sentence<Word>::const_iterator;

typedef int64_t Int;
typedef int32_t Id;
typedef std::pair<Id, Id> Edge;

// defaults defined here for consistency
namespace def {

const int DIMENSION = 100;
const int EPOCHS = 1;
const Float LEARNING_RATE = 0.025;
const int CONTEXT_SIZE = 5;
const bool DYNAMIC_CONTEXT = true;
const int NEGATIVE_SAMPLES = 5;
const bool VERBOSE = true;
const Float SUMBSAMPLING_FACTOR = 0.75;
const bool BINARY = false;
const Float BACKTRACK_PROBABILITY = 0.0;
const int WALK_LENGTH = 80;
const int WALKS_PER_NODE = 10;

} // namespace def


} // namespace emb
