import unittest
import os
import shutil
from Pagerank import pagerank

class TestPagerank(unittest.TestCase):
    def setUp(self):
        self.tmpDir = 'tmp'
        self.inputPath = os.path.join(self.tmpDir, 'input')
        self.outputPath = os.path.join(self.tmpDir, 'output')

        if not os.path.exists(self.tmpDir):
            os.makedirs(self.tmpDir)

        open(self.inputPath, 'w').close()

    def tearDown(self):
        if os.path.isdir(self.tmpDir):
            shutil.rmtree(self.tmpDir)

    def testPagerank_SimpleCase(self):
        with open(self.inputPath, 'w') as input_:
            input_.write("1 2\n")
            input_.write("2 1\n")

            pagerank(self.inputPath, self.outputPath)

            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()