#!/usr/bin/env python
import zoom
import unittest

class TestPoint(unittest.TestCase):
    def test_constructor(self):
        point = zoom.Point(1.0, 1.0)
        self.assertIs(type(point), zoom.Point)

    def test_accessors(self):
        point = zoom.Point(1.0, 1.0)
        self.assertEqual(point.x, 1.0)
        self.assertEqual(point.y, 1.0)

        point.x = 2.0
        point.y = 2.0

        self.assertEqual(point.x, 2.0)
        self.assertEqual(point.y, 2.0)

class TestBounds(unittest.TestCase):
    def test_constructor(self):
        bounds = zoom.Bounds(zoom.Point(1, 1), zoom.Point(1, 1))
        self.assertIs(type(bounds), zoom.Bounds)

class TestZoom(unittest.TestCase):
    def test_constructor(self):
        points = [zoom.Point(0, 0), zoom.Point(1, 0), zoom.Point(1, 1), zoom.Point(0, 1)]
        z = zoom.Zoom(points, 100)
        self.assertIs(type(z), zoom.Zoom)


if __name__ == '__main__':
    unittest.main()