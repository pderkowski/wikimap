#include <string>
#include <vector>
#include <iostream>
#include <stdexcept>
#include <limits>
#include <boost/python.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

class RecordParser {
public:
    RecordParser(const std::string& text)
    : text_(text), position_(1)
    { }

    long long consumeIntegerField();
    std::string consumeTextField();

    void moveToNextRecord();

    bool done() const { return position_ >= text_.size(); }

private:
    size_t findNextUnescapedQuote(size_t pos) const;
    std::string unescapeString(const std::string& str) const;

    void checkedMove(size_t position_, int offset);

    std::string text_;
    size_t position_;

};

long long RecordParser::consumeIntegerField() {
    auto end = text_.find_first_of(",)", position_);
    long long res;
    try {
        res = std::stoll(text_.substr(position_, end - position_));
    } catch (const std::exception& e) {
        std::string context = text_.substr(std::max(0, (int)position_ - 100), 250);
        std::cout << context << std::endl;
        std::cout << text_.substr(position_, end - position_) << std::endl;
        throw;
    }

    if (text_[end] == ',')
        checkedMove(end, 1); // move to next after ,
    else
        checkedMove(end, -1); // move to the end of the record

    return res;
}

std::string RecordParser::consumeTextField() {
    auto end = findNextUnescapedQuote(position_ + 1); // skip opening '
    std::string res = unescapeString(text_.substr(position_ + 1, end - position_ - 1)); // skip opening and enclosing '
    checkedMove(end, 2); // move to next after ',
    return res;
}

void RecordParser::moveToNextRecord() {
    size_t end = text_.find("),(", position_); // careful! this can fail if not all the text fields of the record have been consumed
    checkedMove(end, 3); // move to next after ),(
}

size_t RecordParser::findNextUnescapedQuote(size_t pos) const {
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
std::string RecordParser::unescapeString(const std::string& str) const {
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

void RecordParser::checkedMove(size_t pos, int offset) {
    position_ = pos;
    if (offset >= 0) {
        position_ += std::min(std::numeric_limits<size_t>::max() - position_, static_cast<size_t>(offset));
    } else {
        position_ -= std::min(position_ - std::numeric_limits<size_t>::min(), static_cast<size_t>(-offset));
    }
}


typedef long long INTEGER;
typedef std::string TEXT;

struct PageRecord {
public:
    PageRecord() = default;

    PageRecord(RecordParser& parser)
    : id(parser.consumeIntegerField()), ns(parser.consumeIntegerField()), title(parser.consumeTextField())
    { }

    INTEGER id;
    INTEGER ns;
    TEXT title;

    bool operator == (const PageRecord& other) const { return id == other.id && ns == other.ns && title == other.title; }
};

struct LinksRecord {
public:
    LinksRecord() = default;

    LinksRecord(RecordParser& parser)
    : from(parser.consumeIntegerField()), ns(parser.consumeIntegerField()), title(parser.consumeTextField()), from_ns(parser.consumeIntegerField())
    { }

    INTEGER from;
    INTEGER ns;
    TEXT title;
    INTEGER from_ns;

    bool operator == (const LinksRecord& other) const { return from == other.from && ns == other.ns && title == other.title && from_ns == other.from_ns; }
};

template<class Record>
std::vector<Record> parseValues(const std::string& values) {
    RecordParser parser(values);

    std::vector<Record> records;
    while (!parser.done()) {
        records.push_back(Record(parser));
        parser.moveToNextRecord();
    }

    return records;
}

namespace py = boost::python;

BOOST_PYTHON_MODULE(libsqltools)
{
    py::class_<PageRecord>("PageRecord")
        .def_readwrite("id", &PageRecord::id)
        .def_readwrite("ns", &PageRecord::ns)
        .def_readwrite("title", &PageRecord::title);

    py::class_<LinksRecord>("LinksRecord")
        .def_readwrite("from_", &LinksRecord::from) // from is a python keyword, don't delete the underscore
        .def_readwrite("ns", &LinksRecord::ns)
        .def_readwrite("title", &LinksRecord::title)
        .def_readwrite("from_ns", &LinksRecord::from_ns);

    py::class_<std::vector<PageRecord>>("PageRecordList").def(py::vector_indexing_suite<std::vector<PageRecord>>());
    py::class_<std::vector<LinksRecord>>("LinksRecordList").def(py::vector_indexing_suite<std::vector<LinksRecord>>());

    py::def("parsePageValues", parseValues<PageRecord>);
    py::def("parseLinksValues", parseValues<LinksRecord>);
}