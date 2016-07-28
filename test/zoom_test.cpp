#include "catch.hpp"
#include "zoom.hpp"
#include "partitiontree.hpp"

bool pointIn(const Point& p, const std::vector<Point>& points) {
    return std::find(points.begin(), points.end(), p) != points.end();
}

TEST_CASE("Zoom can select points within given bounds on a given level", "[zoom]") {
    std::vector<Point> points;
    for (int i = 0; i < 8; i += 4) {
        for (int j = 0; j < 8; j += 4) {
            points.push_back(Point(i, j));
        }
    }

    for (int i = 0; i < 8; i += 2) {
        for (int j = 0; j < 8; j += 2) {
            if (i % 4 != 0 || j % 4 != 0) {
                points.push_back(Point(i, j));
            }
        }
    }

    for (int i = 0; i < 8; i += 1) {
        for (int j = 0; j < 8; j += 1) {
            if (i % 2 != 0 || j % 2 != 0) {
                points.push_back(Point(i, j));
            }
        }
    }

    REQUIRE(points.size() == 64);

    Zoom zoom(points, 4);

    SECTION("Bounds is the entire space") {
        Bounds bounds = helpers::getBounds(points);

        auto lvl0 = zoom.getPoints(bounds, 0);

        REQUIRE(lvl0.size() == 4);
        REQUIRE(std::all_of(points.begin(), points.begin()+4, [&lvl0] (const Point& p) {
            return pointIn(p, lvl0);
        })==true);

        auto lvl1 = zoom.getPoints(bounds, 1);
        REQUIRE(lvl1.size() == 16);
        REQUIRE(std::all_of(points.begin(), points.begin()+16, [&lvl1] (const Point& p) {
            return pointIn(p, lvl1);
        })==true);

        auto lvl2 = zoom.getPoints(bounds, 2);
        REQUIRE(lvl2.size() == 64);
        REQUIRE(std::all_of(points.begin(), points.begin()+64, [&lvl2] (const Point& p) {
            return pointIn(p, lvl2);
        })==true);
    }

    SECTION("Bounds is a part of the space") {
        Bounds bounds(Point(3, 5), Point(7, 7));

        auto lvl0 = zoom.getPoints(bounds, 0);
        REQUIRE(lvl0.size() == 4);

        auto lvl1 = zoom.getPoints(bounds, 1);
        REQUIRE(lvl1.size() == 8); // only half of points at lvl 1

        auto lvl2 = zoom.getPoints(bounds, 2);
        REQUIRE(lvl2.size() == 24);

        auto lvl3 = zoom.getPoints(bounds, 3);
        REQUIRE(lvl3.size() == 24); // lvl 2 already showed all the points, so lvl 3 doesnt not increasy granularity
    }
}