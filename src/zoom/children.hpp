#pragma once

#include <array>

class Node;

class Children {
private:
    std::array<Node*, 4> children_;
public:
    typedef typename decltype(children_)::iterator iterator;
    typedef typename decltype(children_)::const_iterator const_iterator;
public:
    Children() : children_{ nullptr, nullptr, nullptr, nullptr } { }

    iterator begin() { return children_.begin(); }
    iterator end() { return children_.end(); }

    const_iterator begin() const { return children_.begin(); }
    const_iterator end() const { return children_.end(); }

    void setTopLeft(Node* tl) { children_[0] = tl; }
    void setTopRight(Node* tr) { children_[1] = tr; }
    void setBottomRight(Node* br) { children_[2] = br; }
    void setBottomLeft(Node* bl) { children_[3] = bl; }

    const Node* getTopLeft() const { return children_[0]; }
    const Node* getTopRight() const { return children_[1]; }
    const Node* getBottomRight() const { return children_[2]; }
    const Node* getBottomLeft() const { return children_[3]; }

    Node* getTopLeft() { return children_[0]; }
    Node* getTopRight() { return children_[1]; }
    Node* getBottomRight() { return children_[2]; }
    Node* getBottomLeft() { return children_[3]; }
};
