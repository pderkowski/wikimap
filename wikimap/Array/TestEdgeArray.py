#!/usr/bin/env python

from EdgeArray import EdgeArray
import os

class TestArray(object):
    edges = [
        (0, 1),
        (0, 2),
        (0, 2),
        (3, 1),
        (3, 3),
        (1, 2),
        (2, 1),
        (4, 6),
        (6, 0),
        (3, 4)
    ]

    storage = 'tmptestfile'

    def __enter__(self):
        ea = EdgeArray(TestArray.storage)
        ea.populate(TestArray.edges)
        return ea

    def __exit__(self, *args):
        os.unlink(TestArray.storage)

def check(message, condition):
    if condition:
        print "[PASS] ", message
    else:
        print "[FAIL] ", message

def printEdgeArray(ea):
    for e in ea:
        print e

def testBasics():
    with TestArray() as ea:
        check("Basic test", list(ea) == TestArray.edges)

def testSortByStartNode():
    with TestArray() as ea:
        ea.sortByStartNode()
        check("Sort by start node", [node[0] for node in ea] == [0, 0, 0, 1, 2, 3, 3, 3, 4, 6])

def testSortByEndNode():
    with TestArray() as ea:
        ea.sortByEndNode()
        check("Sort by end node", [node[1] for node in ea] == [0, 1, 1, 1, 2, 2, 2, 3, 4, 6])

def testFilterByNodes():
    with TestArray() as ea:
        ea.filterByNodes(range(1, 7))
        check("Filter by nodes", list(ea) == [(3, 1), (3, 3), (1, 2), (2, 1), (4, 6), (3, 4)])

def testInverseEdges():
    with TestArray() as ea:
        ea.inverseEdges()
        check("Inverse edges", list(ea) == [(e[1], e[0]) for e in TestArray.edges])

def main():
    print "Testing python bindings:"
    testBasics()
    testSortByStartNode()
    testSortByEndNode()
    testFilterByNodes()
    testInverseEdges()

if __name__ == "__main__":
    main()
