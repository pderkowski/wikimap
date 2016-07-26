#include <cassert>
#include "quadtree.hpp"
#include "node.hpp"

Quadtree::Quadtree(const Bounds& bounds, int nodeCapacity)
: root_(new Node(bounds, nodeCapacity))
{ }

Quadtree::~Quadtree() {
    delete root_;
}

void Quadtree::insert(const Point& p) {
    root_->insert(p);
}

std::vector<Point> Quadtree::getPointsNearby(const Point& p, int level) const {
    assert(level >= 0);
    assert(root_->contains(p));

    Node* current = root_;
    while (!current->isLeaf() && level > 0) {
        current = current->getChildContainingPoint(p);
        --level;
    }

    return current->getPoints();
}