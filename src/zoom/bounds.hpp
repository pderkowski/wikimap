#pragma once

#include <array>
#include <vector>

struct Point {
    Point(double x, double y);

    double x;
    double y;
};

bool operator == (const Point& lhs, const Point& rhs);

class Bounds {
public:
    Bounds(const Point& topLeft, const Point& bottomRight);

    bool contain(const Point& p) const;

    Bounds getTopLeftQuadrant() const;
    Bounds getTopRightQuadrant() const;
    Bounds getBottomRightQuadrant() const;
    Bounds getBottomLeftQuadrant() const;

    std::array<Point, 4> getCorners() const;

private:
    Point topLeft_;
    Point bottomRight_;

private:
    friend bool operator == (const Bounds& lhs, const Bounds& rhs);
};

bool operator == (const Bounds& lhs, const Bounds& rhs);


namespace helpers {
    Bounds getBounds(const std::vector<Point>& points);
}