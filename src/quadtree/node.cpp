#include "node.hpp"
#include <cassert>
#include <algorithm>

Node::Node(const Bounds& bounds, int capacity)
: children_(), bounds_(bounds), points_(), capacity_(capacity)
{
    assert(capacity_ > 0);
}

Node::~Node() {
    for (auto c : children_) {
        delete c;
    }
}

bool Node::isLeaf() const {
    assert(std::all_of(children_.begin(), children_.end(), [] (const Node* c) {return c != nullptr;})  // either have 4 valid children
        || std::all_of(children_.begin(), children_.end(), [] (const Node* c) {return c == nullptr;})); // or 0


    return std::all_of(children_.begin(), children_.end(), [] (const Node* c) {return c == nullptr;});
}

bool Node::isFull() const {
    return points_.size() >= capacity_;
}

bool Node::contains(const Point& p) const {
    return bounds_.contain(p);
}

const Node* Node::getChildContainingPoint(const Point& p) const {
    assert(!isLeaf());
    assert(contains(p));

    for (const auto& child : children_) {
        if (child->contains(p))
            return child;
    }

    assert(0);
}

Node* Node::getChildContainingPoint(const Point& p) {
    return const_cast<Node*>(static_cast<const Node*>(this)->getChildContainingPoint(p));
}

void Node::split() {
    assert(isLeaf());

    children_.setTopLeft(new Node(bounds_.getTopLeftQuadrant(), capacity_));
    children_.setTopRight(new Node(bounds_.getTopRightQuadrant(), capacity_));
    children_.setBottomRight(new Node(bounds_.getBottomRightQuadrant(), capacity_));
    children_.setBottomLeft(new Node(bounds_.getBottomLeftQuadrant(), capacity_));

    auto tl = children_.getTopLeft();
    auto tr = children_.getTopRight();
    auto br = children_.getBottomRight();
    auto bl = children_.getBottomLeft();

    for (const auto& p : points_) {
        if (tl->contains(p)) {
            tl->insert(p);
        } else if (tr->contains(p)) {
            tr->insert(p);
        } else if (br->contains(p)) {
            br->insert(p);
        } else if (bl->contains(p)) {
            bl->insert(p);
        } else {
            assert(0);
        }
    }
}

void Node::insert(const Point& p) {
    if (isFull()) {
        if (isLeaf()) {
            split();
        }

        assert(!isLeaf());
        getChildContainingPoint(p)->insert(p);
    } else {
        assert(!isFull());
        assert(isLeaf());
        points_.push_back(p);
    }
}