import unittest
import os
import subprocess

from Pagerank import pagerank

class TestBinding(unittest.TestCase):
    def runTest(self):
        input_ = "1 2\n2 3\n3 1\n"
        output = pagerank(input_, verbosity=0)

        self.assertEqual(len(list(output)), 3)

if __name__ == '__main__':
    unittest.main()