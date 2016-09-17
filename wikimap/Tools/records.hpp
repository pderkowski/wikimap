#pragma once

#include <string>
#include "parser.hpp"

struct PageRecord {
public:
    // PageRecord() = default;

    PageRecord(Parser& parser);

    INTEGER id;
    INTEGER ns;
    TEXT title;

    // bool operator == (const PageRecord& other) const { return id == other.id && ns == other.ns && title == other.title; }
};

struct LinksRecord {
public:
    // LinksRecord() = default;

    LinksRecord(Parser& parser);

    INTEGER from;
    INTEGER ns;
    TEXT title;
    INTEGER from_ns;

    // bool operator == (const LinksRecord& other) const { return from == other.from && ns == other.ns && title == other.title && from_ns == other.from_ns; }
};