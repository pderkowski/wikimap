#pragma once

#include <string>
#include "parser.hpp"

struct PageRecord {
public:
    PageRecord(Parser& parser);

    INTEGER id;
    INTEGER ns;
    TEXT title;
};

struct LinksRecord {
public:
    LinksRecord(Parser& parser);

    INTEGER from;
    INTEGER ns;
    TEXT title;
    INTEGER from_ns;
};

struct CategoryRecord {
public:
    CategoryRecord(Parser& parser);

    INTEGER id;
    TEXT title;
};

struct CategoryLinksRecord {
public:
    CategoryLinksRecord(Parser& parser);

    INTEGER from;
    TEXT to;
};