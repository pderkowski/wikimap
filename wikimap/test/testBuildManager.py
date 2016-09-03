import unittest
import os
import shutil
import logging
from BuildManager import BuildManager

class DummyJob(object):
    def __init__(self, name, inputs, outputs):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.skipped = True
        self.duration = 0
        self.outcome = ''

    def reset(self):
        self.skipped = True

    def run(self, outputDirectory, config):
        self.skipped = False
        for o in self.outputs:
            open(os.path.join(outputDirectory, o), 'w').close() # create empty file

    def skip(self):
        self.skipped = True

class BuildDirectoryCreation(unittest.TestCase):
    def __init__(self, subdirs, *args, **kwargs):
        super(BuildDirectoryCreation, self).__init__(*args, **kwargs)
        self.archiveDir = 'build'
        self.subdirs = subdirs
        self.manager = BuildManager(self.archiveDir)

    def setUp(self):
        if not os.path.exists(self.archiveDir):
            os.makedirs(self.archiveDir)

        for s in self.subdirs:
            path = os.path.join(self.archiveDir, s)
            if not os.path.exists(path):
                os.makedirs(path)

    def tearDown(self):
        if os.path.isdir(self.archiveDir):
            shutil.rmtree(self.archiveDir)

class BuildDirectoryCreation_SimpleCase(BuildDirectoryCreation):
    def __init__(self, *args, **kwargs):
        super(BuildDirectoryCreation_SimpleCase, self).__init__(['build0', 'build1'], *args, **kwargs)

    def runTest(self):
        self.manager.run([], {})
        self.assertTrue(os.path.exists('build/build2'))

class BuildDirectoryCreation_DirectoryEmpty(BuildDirectoryCreation):
    def __init__(self, *args, **kwargs):
        super(BuildDirectoryCreation_DirectoryEmpty, self).__init__([], *args, **kwargs)

    def runTest(self):
        self.manager.run([], {})
        self.assertTrue(os.path.exists('build/build0'))

class BuildDirectoryCreation_CheckOnlyPrefixed(BuildDirectoryCreation):
    def __init__(self, *args, **kwargs):
        super(BuildDirectoryCreation_CheckOnlyPrefixed, self).__init__(['build0', 'build1', 'test3'], *args, **kwargs)

    def runTest(self):
        self.manager.run([], {})
        self.assertTrue(os.path.exists('build/build2'))

class BuildDirectoryCreation_MultipleRuns(BuildDirectoryCreation):
    def __init__(self, *args, **kwargs):
        super(BuildDirectoryCreation_MultipleRuns, self).__init__([], *args, **kwargs)

    def runTest(self):
        self.assertFalse(os.path.exists('build/build0'))
        self.manager.run([], {})
        self.assertTrue(os.path.exists('build/build0'))

        self.assertFalse(os.path.exists('build/build1'))
        self.manager.run([], {})
        self.assertTrue(os.path.exists('build/build1'))

class BuildDirectoryCreation_ConfigFileIsCreated(BuildDirectoryCreation):
    def __init__(self, *args, **kwargs):
        super(BuildDirectoryCreation_ConfigFileIsCreated, self).__init__([], *args, **kwargs)

    def runTest(self):
        self.manager.run([], {})
        self.assertTrue(os.path.exists('build/build0/config'))

class BuildCourse(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BuildCourse, self).__init__(*args, **kwargs)
        self.archiveDir = 'build'
        self.manager = BuildManager(self.archiveDir)

    def prepare(self, build, config):
        self.manager.run(build, config)
        for j in build:
            j.reset()

    def setUp(self):
        if not os.path.exists(self.archiveDir):
            os.makedirs(self.archiveDir)

    def tearDown(self):
        if os.path.isdir(self.archiveDir):
            shutil.rmtree(self.archiveDir)

class BuildCourse_RunAllJobsIfNoPreviousBuilds(BuildCourse):
    def __init__(self, *args, **kwargs):
        super(BuildCourse_RunAllJobsIfNoPreviousBuilds, self).__init__(*args, **kwargs)

    def runTest(self):
        job1 = DummyJob('job1', [], ['job1'])
        job2 = DummyJob('job2', ['job1'], ['job2'])
        build = [job1, job2]
        self.manager.run(build, {})

        self.assertTrue(all(not j.skipped for j in build))

class BuildCourse_SkipAllJobsIfTheSameBuildAndConfig(BuildCourse):
    def __init__(self, *args, **kwargs):
        super(BuildCourse_SkipAllJobsIfTheSameBuildAndConfig, self).__init__(*args, **kwargs)

    def runTest(self):
        job1 = DummyJob('job1', [], ['job1'])
        job2 = DummyJob('job2', ['job1'], ['job2'])
        build = [job1, job2]
        config = { 'job1': { 'a': 'a' }, 'job2': { 'b': 'b' } }
        self.prepare(build, config)
        self.manager.run(build, config)
        self.assertTrue(all(j.skipped for j in build))

class BuildCourse_ChangedJobsCascadeToDependants(BuildCourse):
    def __init__(self, *args, **kwargs):
        super(BuildCourse_ChangedJobsCascadeToDependants, self).__init__(*args, **kwargs)

    def runTest(self):
        job1 = DummyJob('job1', [], ['job1'])
        job2 = DummyJob('job2', ['job1'], ['job2a', 'job2b'])
        job3 = DummyJob('job3', ['job2a'], ['job3'])
        job4 = DummyJob('job4', ['job2b'], ['job4'])
        job5 = DummyJob('job5', ['job1'], ['job5'])
        job6 = DummyJob('job6', ['job5', 'job2a'], [])

        build = [job1, job2, job3, job4, job5, job6]
        self.prepare(build, {})

        self.manager.run(build, { 'job2': { 'a': 'a' } })

        self.assertTrue(job1.skipped)
        self.assertFalse(job2.skipped)
        self.assertFalse(job3.skipped)
        self.assertFalse(job4.skipped)
        self.assertTrue(job5.skipped)
        self.assertFalse(job6.skipped)

class BuildCourse_RunIfOutputsFromLastBuildAreMissing(BuildCourse):
    def __init__(self, *args, **kwargs):
        super(BuildCourse_RunIfOutputsFromLastBuildAreMissing, self).__init__(*args, **kwargs)

    def runTest(self):
        job1 = DummyJob('job1', [], ['job1'])
        job2 = DummyJob('job2', ['job1'], ['job2'])

        build = [job1, job2]
        self.prepare(build, {})

        path = os.path.join(self.archiveDir, 'build0', 'job2')
        self.assertTrue(os.path.exists(path))
        os.remove(path)

        self.manager.run(build, {})

        self.assertTrue(job1.skipped)
        self.assertFalse(job2.skipped)

if __name__ == '__main__':
    unittest.main()