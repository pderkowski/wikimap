#pragma once

#include "bounds.hpp"
#include "children.hpp"
#include <vector>

class Node {
public:
    Node(const Bounds& bounds, int capacity);
    Node(const Node& other) = delete;
    Node& operator = (const Node& other) = delete;
    ~Node();

    const Children& getChildren() const { return children_; }
    Children& getChildren() { return children_; }

    const Node* getChildContainingPoint(const Point& p) const;
    Node* getChildContainingPoint(const Point& p);

    std::vector<Point> getPoints() const { return points_; }

    bool isLeaf() const;
    bool contains(const Point& p) const;

    void insert(const Point& p);

private:
    bool isFull() const;

    void split();

    Children children_;

    Bounds bounds_;
    std::vector<Point> points_;

    int capacity_;
};
