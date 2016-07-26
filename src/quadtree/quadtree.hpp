#pragma once

#include <vector>
#include <array>
#include "bounds.hpp"

class Node;

class Quadtree {
public:
    Quadtree(const Bounds& bounds, int nodeCapacity);

    Quadtree(const Quadtree& other) = delete;
    Quadtree& operator = (const Quadtree& other) = delete;

    ~Quadtree();

    void insert(const Point& p);

    std::vector<Point> getPointsNearby(const Point& p, int level) const;

private:
    Node* root_;
};


