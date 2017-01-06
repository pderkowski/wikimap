import os
import Utils
import logging
import sys
import errno
import Paths

def getImmediateSubdirectories(directory):
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

class BuildManager(object):
    def __init__(self, archiveDir):
        self._archiveDir = archiveDir
        self._buildPrefix = 'build'

        self.lastBuild = self._getLastBuild()
        self.newBuild = self._getNewBuild()

        self._lastConfig = self._getLastConfig()
        self._newConfig = os.path.join(self.newBuild, 'config')

    def run(self, build):
        logger = logging.getLogger(__name__)

        self._createDirs()

        changedFiles = set()
        summary = []
        config = {}

        logger.info('STARTING BUILD IN {}'.format(self.newBuild))

        for job in build:
            if job.noskip \
            or self._inputsChanged(job, changedFiles) \
            or self._configChanged(job) \
            or not self._outputsComputed(job) \
            or not self._artifactsComputed(job):
                logger.info('STARTING JOB: {}'.format(job.name))

                changedFiles.update(job.outputs)

                try:
                    job.run()
                    summary.append((job.outcome, job.name, job.duration))
                    config[job.name] = job.config
                except KeyboardInterrupt:
                    summary.append((job.outcome, job.name, job.duration))
                    self._printSummary(summary)
                    Utils.saveToFile(self._newConfig, config)
                    sys.exit(1)
                except Exception, e:
                    logger.exception(str(e))
                    summary.append((job.outcome, job.name, job.duration))
                    self._printSummary(summary)
                    Utils.saveToFile(self._newConfig, config)
                    sys.exit(1)
            else:
                logger.info('SKIPPING JOB: {}'.format(job.name))

                job.skip()
                summary.append((job.outcome, job.name, job.duration))
                config[job.name] = job.config

                self._makeLinks(job.outputs)
                self._makeLinks(job.artifacts)

        self._printSummary(summary)
        Utils.saveToFile(self._newConfig, config)

    def _outputsComputed(self, job):
        return self.lastBuild and all(os.path.exists(o) for o in Paths.resolve(job.outputs, base=self.lastBuild))

    def _artifactsComputed(self, job):
        return self.lastBuild and all(os.path.exists(a) for a in Paths.resolve(job.artifacts, base=self.lastBuild))

    def _inputsChanged(self, job, changedFiles):
        return any(input_ in changedFiles for input_ in Paths.resolve(job.inputs))

    def _configChanged(self, job):
        lastTargetConfig = self._lastConfig.get(job.name, {})
        currentTargetConfig = job.config
        return lastTargetConfig != currentTargetConfig

    def _makeLinks(self, paths):
        old = Paths.resolve(paths, base=self.lastBuild)
        new = Paths.resolve(paths)

        for src, dst in zip(old, new):
            try:
                Utils.linkDirectory(src, dst)
            except OSError as exc: # python >2.5
                if exc.errno == errno.ENOTDIR:
                    os.link(src, dst)
                else: raise

    def _createDirs(self):
        if not os.path.exists(self._archiveDir):
            os.makedirs(self._archiveDir)

        if not os.path.exists(self.newBuild):
            os.makedirs(self.newBuild)

    def _getNewBuild(self):
        return os.path.join(self._archiveDir, self._buildPrefix + str(self._getBuildIndex()))

    def _getLastBuild(self):
        lastIndex = self._getLastBuildIndex()
        if lastIndex is not None:
            return os.path.join(self._archiveDir, self._buildPrefix + str(lastIndex))
        else:
            return None

    def _getLastConfig(self):
        if self.lastBuild is not None:
            path = os.path.join(self.lastBuild, 'config')
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

    def _getIndex(self, dir_):
        suffixStr = dir_[len(self._buildPrefix):]
        return int(suffixStr)

    def _getBuildIndex(self):
        last = self._getLastBuildIndex()
        if last is None:
            return 0
        else:
            return last + 1

    def _printSummary(self, summary):
        logger = logging.getLogger(__name__)

        summaryStr = '\n\n'

        summaryStr += '-'*80+'\n'
        summaryStr += '{:35} |  OUTCOME  |  DURATION   |'.format('JOB SUMMARY')+'\n'
        summaryStr += '-'*80+'\n'

        OKGREEN = '\033[92m'
        OKBLUE = '\033[94m'
        FAILRED = '\033[91m'
        ENDCOLOR = '\033[0m'
        WARNING = '\033[93m'

        for outcome, title, duration in summary:
            if outcome == 'SUCCESS':
                COLOR = OKGREEN
            elif outcome == 'FAILURE':
                COLOR = FAILRED
            elif outcome == 'SKIPPED':
                COLOR = OKBLUE
            else:
                COLOR = WARNING

            summaryStr += '{:35} | {}[{}]{} | {} |'.format(title, COLOR, outcome, ENDCOLOR, Utils.formatDuration(duration))+'\n'

        summaryStr += '-'*80+'\n'

        logger.info(summaryStr)
