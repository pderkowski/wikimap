#pragma once

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

private:
    Point topLeft_;
    Point bottomRight_;
};
