#pragma once

#include <cstdint>
#include <vector>
#include <utility>


namespace w2v {


typedef float Float;
typedef std::vector<Float> Embedding;
typedef int64_t Int;
typedef int32_t Token;
typedef std::vector<Token> Sequence;
typedef typename Sequence::const_iterator SequenceIterator;
typedef std::pair<SequenceIterator, SequenceIterator> SequenceRange;


}
