#include "catch.hpp"
#include "partitiontree.hpp"
#include "bounds.hpp"
#include <iostream>

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

    SECTION("If a bucket at a specified level does not exist, a containing bucket is returned") {
        auto lvl0 = pt.getBucket(Point(3, 3), 0);
        auto lvl1 = pt.getBucket(Point(3, 3), 1);
        auto lvl2 = pt.getBucket(Point(3, 3), 2);

        REQUIRE((lvl0.getPoints().size() == 1 && lvl0.getPoints()[0] == Point(2, 2)) == true);
        REQUIRE((lvl1.getPoints().size() == 1 && lvl1.getPoints()[0] == Point(2, 2)) == true);
        REQUIRE((lvl2.getPoints().size() == 1 && lvl2.getPoints()[0] == Point(2, 2)) == true);
    }
}

TEST_CASE("PartitionTree::getBucketCoords returns correct bucket coords", "[partitiontree]") {
    PartitionTree pt(Bounds(Point(0, 0), Point(8, 8)), 1);

    std::vector<Point> points;
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            points.push_back(Point(i, j));
        }
    }

    REQUIRE(std::all_of(points.begin(), points.end(), [&pt] (const Point& p) {
        auto coords = pt.getBucketCoords(p, 0);
        return coords.x() == 0 && coords.y() == 0 && coords.level() == 0;
    })==true);

    REQUIRE(std::all_of(points.begin(), points.end(), [&pt] (const Point& p) {
        auto coords = pt.getBucketCoords(p, 1);
        return coords.x() == ((int)p.x / 4) && coords.y() == ((int)p.y / 4) && coords.level() == 1;
    })==true);

    REQUIRE(std::all_of(points.begin(), points.end(), [&pt] (const Point& p) {
        auto coords = pt.getBucketCoords(p, 2);
        return coords.x() == ((int)p.x / 2) && coords.y() == ((int)p.y / 2) && coords.level() == 2;
    })==true);

    REQUIRE(std::all_of(points.begin(), points.end(), [&pt] (const Point& p) {
        auto coords = pt.getBucketCoords(p, 3);
        return coords.x() == ((int)p.x) && coords.y() == ((int)p.y) && coords.level() == 3;
    })==true);
}