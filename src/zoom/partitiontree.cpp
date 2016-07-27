#include <cassert>
#include "partitiontree.hpp"
#include "node.hpp"

Bucket::Bucket(const Node* node, int level)
: bucketNode_(node), level_(level)
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
    assert(level >= 0);
    assert(root_->contains(p));

    int actualLevel = 0;

    Node* current = root_;
    while (!current->isLeaf() && actualLevel < level) {
        current = current->getChildContainingPoint(p);
        ++actualLevel;
    }

    return Bucket(current, actualLevel);
}

