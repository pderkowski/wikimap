import os
import Utils

def getImmediateSubdirectories(directory):
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

class BuildManager(object):
    def __init__(self, archiveDir):
        self._archiveDir = archiveDir
        self._buildPrefix = 'build'

    def run(self, build, config):
        self._lastDir = self._getLastDir()
        self._lastConfig = self._getLastConfig()
        self._buildDir = self._getBuildDir()

        if not os.path.exists(self._buildDir):
            os.makedirs(self._buildDir)

        Utils.saveToFile(os.path.join(self._buildDir, 'config'), config)

        changedFiles = set()
        for job in build:
            if self._inputsChanged(job.inputs, changedFiles) or self._configChanged(config, job.name) or not self._outputsComputed(job):
                changedFiles.update(job.outputs)
                jobConfig = config.get(job.name, {})
                job.run(jobConfig, self._buildDir)
            else:
                self._makeLinks(job.outputs)

    def _outputsComputed(self, job):
        return self._lastDir and all(os.path.exists(os.path.join(self._lastDir, o)) for o in job.outputs)

    def _inputsChanged(self, inputs, changedFiles):
        return any(input_ in changedFiles for input_ in inputs)

    def _configChanged(self, config, jobName):
        lastTargetConfig = self._lastConfig.get(jobName, {})
        currentTargetConfig = config.get(jobName, {})
        return lastTargetConfig != currentTargetConfig

    def _makeLinks(self, filenames):
        for f in filenames:
            os.link(os.path.join(self._lastDir, f), os.path.join(self._buildDir, f))

    def _getBuildDir(self):
        return os.path.join(self._archiveDir, self._buildPrefix + str(self._getBuildIndex()))

    def _getLastDir(self):
        lastIndex = self._getLastBuildIndex()
        if lastIndex is not None:
            return os.path.join(self._archiveDir, self._buildPrefix + str(lastIndex))
        else:
            return None

    def _getLastConfig(self):
        if self._lastDir is not None:
            path = os.path.join(self._lastDir, 'config')
            if os.path.exists(path):
                return Utils.loadFromFile(path)

        return {}

    def _getLastBuildIndex(self):
        subdirs = getImmediateSubdirectories(self._archiveDir)
        buildSubdirs = [d for d in subdirs if d.startswith(self._buildPrefix)]

        bestI = None
        bestSuffix = None
        for i, s in enumerate(buildSubdirs):
            try:
                suffix = self._getIndex(s)
                if bestSuffix is None or suffix > bestSuffix:
                    bestI = i
                    bestSuffix = suffix
            except ValueError:
                pass

        if bestI is not None:
            return self._getIndex(buildSubdirs[bestI])
        else:
            return None

    def _getIndex(self, dir):
        suffixStr = dir[len(self._buildPrefix):]
        return int(suffixStr)

    def _getBuildIndex(self):
        last = self._getLastBuildIndex()
        if last is None:
            return 0
        else:
            return last + 1