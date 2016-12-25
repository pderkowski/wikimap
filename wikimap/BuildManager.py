import os
import Utils
import logging
import sys
import shutil
import errno

def getImmediateSubdirectories(directory):
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

class BuildManager(object):
    def __init__(self, archiveDir):
        self._archiveDir = archiveDir
        self._buildPrefix = 'build'
        self._lastDir = None
        self._lastConfig = None
        self._buildDir = None

    def run(self, build):
        if not os.path.exists(self._archiveDir):
            os.makedirs(self._archiveDir)

        logger = logging.getLogger(__name__)

        self._lastDir = self._getLastDir()
        self._lastConfig = self._getLastConfig()
        self._buildDir = self._getBuildDir()

        if not os.path.exists(self._buildDir):
            os.makedirs(self._buildDir)


        changedFiles = set()
        summary = []
        config = {}

        logger.info('STARTING BUILD IN {}'.format(self._buildDir))

        for job in build:
            if job.noskip \
            or self._inputsChanged(job.inputs, changedFiles) \
            or self._configChanged(job) \
            or not self._outputsComputed(job) \
            or not self._artifactsComputed(job):
                logger.info('STARTING JOB: {}'.format(job.name))

                changedFiles.update(job.outputs)

                try:
                    job.run(self._buildDir)
                    summary.append((job.outcome, job.name, job.duration))
                    config[job.name] = job.config
                except KeyboardInterrupt:
                    summary.append((job.outcome, job.name, job.duration))
                    self._printSummary(summary)
                    Utils.saveToFile(os.path.join(self._buildDir, 'config'), config)
                    sys.exit(1)
                except Exception, e:
                    logger.exception(str(e))
                    summary.append((job.outcome, job.name, job.duration))
                    self._printSummary(summary)
                    Utils.saveToFile(os.path.join(self._buildDir, 'config'), config)
                    sys.exit(1)
            else:
                logger.info('SKIPPING JOB: {}'.format(job.name))

                job.skip()
                summary.append((job.outcome, job.name, job.duration))
                config[job.name] = job.config

                self._makeLinks(job.outputs)
                self._makeLinks(job.artifacts)

        self._printSummary(summary)
        Utils.saveToFile(os.path.join(self._buildDir, 'config'), config)

    def export(self, files, destDir):
        destDir = os.path.realpath(destDir)

        logger = logging.getLogger(__name__)
        logger.info('EXPORTING RESULTS TO {}'.format(destDir))

        if not os.path.isdir(destDir):
            os.makedirs(destDir)

        Utils.clearDirectory(destDir)

        lastBuild = self._getLastDir()
        for f in files:
            src = os.path.join(lastBuild, f)
            dst = os.path.join(destDir, f)

            if os.path.exists(src):
                try:
                    shutil.copytree(src, dst)
                except OSError as exc: # python >2.5
                    if exc.errno == errno.ENOTDIR:
                        shutil.copyfile(src, dst)
                    else: raise

    def _outputsComputed(self, job):
        return self._lastDir and all(os.path.exists(os.path.join(self._lastDir, o)) for o in job.outputs)

    def _artifactsComputed(self, job):
        return self._lastDir and all(os.path.exists(os.path.join(self._lastDir, a)) for a in job.artifacts)

    def _inputsChanged(self, inputs, changedFiles):
        return any(input_ in changedFiles for input_ in inputs)

    def _configChanged(self, job):
        lastTargetConfig = self._lastConfig.get(job.name, {})
        currentTargetConfig = job.config
        return lastTargetConfig != currentTargetConfig

    def _makeLinks(self, filenames):
        for f in filenames:
            src, dst = os.path.join(self._lastDir, f), os.path.join(self._buildDir, f)
            try:
                Utils.linkDirectory(src, dst)
            except OSError as exc: # python >2.5
                if exc.errno == errno.ENOTDIR:
                    os.link(src, dst)
                else: raise

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
