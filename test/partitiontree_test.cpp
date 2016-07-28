#include "catch.hpp"
#include "partitiontree.hpp"
#include "bounds.hpp"

TEST_CASE("Partitiontree creates and gets correct buckets", "[partitiontree]") {
    PartitionTree pt(Bounds(Point(0, 0), Point(4, 4)), 1);

    pt.insert(Point(2, 2));
    pt.insert(Point(1, 1));
    pt.insert(Point(0, 0));

    SECTION("Fine-grained buckets are created when necessary") {
        auto lvl0 = pt.getBucket(Point(0, 0), 0);
        auto lvl1 = pt.getBucket(Point(0, 0), 1);
        auto lvl2 = pt.getBucket(Point(0, 0), 2);

        REQUIRE((lvl0.getPoints().size() == 1 && lvl0.getPoints()[0] == Point(2, 2)) == true);
        REQUIRE((lvl1.getPoints().size() == 1 && lvl1.getPoints()[0] == Point(1, 1)) == true);
        REQUIRE((lvl2.getPoints().size() == 1 && lvl2.getPoints()[0] == Point(0, 0)) == true);
    }

    SECTION ("If a bucket at a specified level does not exist, a containing bucket is returned") {
        auto lvl0 = pt.getBucket(Point(3, 3), 0);
        auto lvl1 = pt.getBucket(Point(3, 3), 1);
        auto lvl2 = pt.getBucket(Point(3, 3), 2);

        REQUIRE((lvl0.getPoints().size() == 1 && lvl0.getPoints()[0] == Point(2, 2)) == true);
        REQUIRE((lvl1.getPoints().size() == 1 && lvl1.getPoints()[0] == Point(2, 2)) == true);
        REQUIRE((lvl2.getPoints().size() == 1 && lvl2.getPoints()[0] == Point(2, 2)) == true);
    }
}

