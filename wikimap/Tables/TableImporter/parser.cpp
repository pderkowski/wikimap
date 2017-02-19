#include "parser.hpp"
#include <iostream>
#include <limits>

long long Parser::consumeIntegerField() {
    auto end = text_.find_first_of(",)", position_);
    long long res;
    try {
        res = std::stoll(text_.substr(position_, end - position_));
    } catch (const std::exception& e) {
        std::string context = text_.substr(std::max(0, (int)position_ - 100), 250);
        std::cerr << context << std::endl;
        std::cerr << text_.substr(position_, end - position_) << std::endl;
        throw;
    }

    if (text_[end] == ',')
        checkedMove(end, 1); // move to next after ,
    else
        checkedMove(end, -1); // move to the end of the record

    return res;
}

std::string Parser::consumeTextField() {
    auto end = findNextUnescapedQuote(position_ + 1); // skip opening '
    std::string res = unescapeString(text_.substr(position_ + 1, end - position_ - 1)); // skip opening and enclosing '
    checkedMove(end, 2); // move to next after ',
    return res;
}

void Parser::moveToNextRecord() {
    size_t end = text_.find("),(", position_); // careful! this can fail if not all the text fields of the record have been consumed
    checkedMove(end, 3); // move to next after ),(
}

size_t Parser::findNextUnescapedQuote(size_t pos) const {
    for (size_t i = pos; pos < text_.size(); ++i) {
        if (text_[i] == '\'') {
            return i;
        } else if (text_[i] == '\\') {
            ++i; // skip escaped character
        }
    }

    return std::string::npos;
}

// only handles MySQL special characters (with the exception of \% and \_ which should not have a special meaning in the dumps)
std::string Parser::unescapeString(const std::string& str) const {
    std::string res;
    res.reserve(str.size());

    char c;
    for (size_t i = 0; i < str.size(); ++i) {
        c = str[i];
        if (c == '\\' && i + 1 < str.size()) {
            ++i;
            c = str[i];

            switch (c) {
                case '0': c = '\0'; break;
                case '\'': c = '\''; break;
                case '\"': c = '\"'; break;
                case 'b': c = '\b'; break;
                case 'n': c = '\n'; break;
                case 'r': c = '\r'; break;
                case 't': c = '\t'; break;
                case 'Z': c = 26; break; // CTRL+Z
                case '\\': c = '\\'; break;
            }
        }
        res.push_back(c);
    }

    return res;
}

void Parser::checkedMove(size_t pos, int offset) {
    position_ = pos;
    if (offset >= 0) {
        position_ += std::min(std::numeric_limits<size_t>::max() - position_, static_cast<size_t>(offset));
    } else {
        position_ -= std::min(position_ - std::numeric_limits<size_t>::min(), static_cast<size_t>(-offset));
    }
}

