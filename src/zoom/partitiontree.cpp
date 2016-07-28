#include <cassert>
#include <cmath>
#include "partitiontree.hpp"
#include "node.hpp"

BucketCoords::BucketCoords(int x, int y, int level)
: x_(x), y_(y), level_(level)
{
    assert(0 <= x_);
    assert(0 <= y_);
    assert(0 <= level_);

    long long p = static_cast<long long>(std::pow(2, level));

    assert(x < p);
    assert(y < p);
}

Bucket::Bucket(const Node* node)
: node_(node)
{ }

PartitionTree::PartitionTree(const Bounds& bounds, int nodeCapacity)
: root_(new Node(bounds, nodeCapacity))
{ }

PartitionTree::~PartitionTree() {
    delete root_;
}

void PartitionTree::insert(const Point& p) {
    root_->insert(p);
}


Bucket PartitionTree::getBucket(const Point& p, int level) const {
    assert(0 <= level);
    assert(root_->contains(p));

    int l = 0;

    Node* current = root_;
    while (!current->isLeaf() && l < level) {
        current = current->getChildContainingPoint(p);
        ++l;
    }

    return Bucket(current);
}

Bucket PartitionTree::getBucket(const BucketCoords& coords) const {
    return getBucket(bucketCoordsToPoint(coords), coords.level());
}

BucketCoords PartitionTree::getBucketCoords(const Point& p, int level) const {
    auto bounds = getBounds();

    int x = 0;
    int y = 0;
    for (int l = 0; l < level; ++l) {
        auto tl = bounds.getTopLeftQuadrant();
        auto tr = bounds.getTopRightQuadrant();
        auto br = bounds.getBottomRightQuadrant();
        auto bl = bounds.getBottomLeftQuadrant();

        if (tl.contain(p)) {
            x *= 2;
            y *= 2;
            bounds = tl;
        } else if (tr.contain(p)) {
            x = 2 * x + 1;
            y *= 2;
            bounds = tr;
        } else if (br.contain(p)) {
            x = 2 * x + 1;
            y = 2 * y + 1;
            bounds = br;
        } else if (bl.contain(p)) {
            x *= 2;
            y = 2 * y + 1;
        } else {
            assert(0);
        }
    }

    return BucketCoords(x, y, level);
}

Point PartitionTree::bucketCoordsToPoint(const BucketCoords& coords) const {
    auto bounds = getBounds();

    int level = 0;
    int p = (int)pow(2, coords.level());
    int x = coords.x();
    int y = coords.y();

    while (level < coords.level()) {
        int half = p / 2;

        if (x < half && y < half) {
            bounds = bounds.getTopLeftQuadrant();
        } else if (x >= half && y < half) {
            bounds = bounds.getTopRightQuadrant();
            x -= half;
        } else if (x >= half && y >= half) {
            bounds = bounds.getBottomRightQuadrant();
            x -= half;
            y -= half;
        } else if (x < half && y >= half) {
            bounds = bounds.getBottomLeftQuadrant();
            y -= half;
        } else {
            assert(0);
        }

        p = half;
        ++level;
    }

    return bounds.getMidpoint();
}