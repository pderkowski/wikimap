#include "records.hpp"
#include "parser.hpp"

PageRecord::PageRecord(Parser& parser)
: id(parser.consumeIntegerField()), ns(parser.consumeIntegerField()), title(parser.consumeTextField())
{ }

LinksRecord::LinksRecord(Parser& parser)
: from(parser.consumeIntegerField()), ns(parser.consumeIntegerField()), title(parser.consumeTextField()), from_ns(parser.consumeIntegerField())
{ }

CategoryRecord::CategoryRecord(Parser& parser)
: id(parser.consumeIntegerField()), title(parser.consumeTextField())
{ }

CategoryLinksRecord::CategoryLinksRecord(Parser& parser)
: from(parser.consumeIntegerField()), to(parser.consumeTextField())
{ }