#pragma once

#include <string>
#include <vector>

typedef long long INTEGER;
typedef std::string TEXT;

class Parser {
public:
    Parser(const std::string& text)  // expected text format: (field, ..., field),(field, ..., field),...,(field, ..., field)
    : text_(text), position_(1)
    { }

    INTEGER consumeIntegerField();
    TEXT consumeTextField();

    void moveToNextRecord();

    bool done() const { return position_ >= text_.size(); }

private:
    size_t findNextUnescapedQuote(size_t pos) const;
    std::string unescapeString(const std::string& str) const;

    void checkedMove(size_t position_, int offset);

    std::string text_;
    size_t position_;
};


template<class Record>
std::vector<Record> parse(const std::string& values) {
    Parser parser(values);

    std::vector<Record> records;
    while (!parser.done()) {
        records.push_back(Record(parser));
        parser.moveToNextRecord();
    }

    return records;
}