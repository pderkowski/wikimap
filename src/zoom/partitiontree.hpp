#pragma once

#include <vector>
#include <array>
#include "bounds.hpp"
#include "node.hpp"

class Bucket {
public:
    Bucket(const Node* node, int level);

    std::vector<Point> getPoints() const { return bucketNode_->getPoints(); }
    Bounds getBounds() const { return bucketNode_->getBounds(); }
    int getLevel() const { return level_; }

private:
    const Node* bucketNode_;
    const int level_;
};

class PartitionTree {
public:
    PartitionTree(const Bounds& bounds, int bucketCapacity);

    PartitionTree(const PartitionTree& other) = delete;
    PartitionTree& operator = (const PartitionTree& other) = delete;

    ~PartitionTree();

    void insert(const Point& p);

    Bucket getBucket(const Point& p, int level) const;
    Bounds getBounds() const { return root_->getBounds(); }

private:
    Node* root_;
};


