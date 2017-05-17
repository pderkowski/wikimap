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


}
