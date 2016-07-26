#include "catch.hpp"
#include "quadtree.hpp"
#include "bounds.hpp"

TEST_CASE("Quadtree insert/get points test", "[Quadtree]") {
    Quadtree qt(Bounds(Point(0, 0), Point(4, 4)), 1);

    qt.insert(Point(2, 2));
    qt.insert(Point(1, 1));
    qt.insert(Point(0, 0));

    SECTION("Lower levels have points nearby") {
        auto lvl0 = qt.getPointsNearby(Point(0, 0), 0);
        auto lvl1 = qt.getPointsNearby(Point(0, 0), 1);
        auto lvl2 = qt.getPointsNearby(Point(0, 0), 2);

        REQUIRE((lvl0.size() == 1 && lvl0[0] == Point(2, 2)) == true);
        REQUIRE((lvl1.size() == 1 && lvl1[0] == Point(1, 1)) == true);
        REQUIRE((lvl2.size() == 1 && lvl2[0] == Point(0, 0)) == true);
    }

    SECTION ("Only top level has points nearby") {
        auto lvl0 = qt.getPointsNearby(Point(3, 3), 0);
        auto lvl1 = qt.getPointsNearby(Point(3, 3), 1);
        auto lvl2 = qt.getPointsNearby(Point(3, 3), 2);

        REQUIRE((lvl0.size() == 1 && lvl0[0] == Point(2, 2)) == true);
        REQUIRE((lvl1.size() == 1 && lvl1[0] == Point(2, 2)) == true);
        REQUIRE((lvl2.size() == 1 && lvl2[0] == Point(2, 2)) == true);
    }
}

