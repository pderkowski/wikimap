import Utils
import Jobs as J
import Builder

LANGUAGES = ['en', 'pl']
DEFAULT_LANGUAGE = 'en'
DEFAULT_TARGET_JOBS = '_ALL_'
DEFAULT_FORCED_JOBS = '_NONE_'


class Build(object):
    def __init__(self, builds_dir, build_prefix, base_build_index, target_jobs,
                 forced_jobs, config):

        self._explorer = Builder.BuildExplorer(builds_dir, build_prefix,
                                               base_build_index)

        if isinstance(config, basestring):
            build_config = Builder.BuildConfig.from_string(config)
        else:
            build_config = Builder.BuildConfig(config)

        # Step 1:
        # Based on some config parameters, select jobs that could possibly be
        # required in a full build.
        build_template = self._get_build_template(build_config)

        # Step 2:
        # Replace textual aliases of jobs with their ordinal numbers in the
        # build template.
        target_jobs = self._resolve_job_aliases(target_jobs, build_template)
        forced_jobs = self._resolve_job_aliases(forced_jobs, build_template)

        # Step 3:
        # Given user's input filter the build to only include requested
        # targets (`target_jobs`) and mark jobs that are to be unconditionally
        # recomputed (`forced_jobs`).
        self._manager = Builder.BuildManager(build_template)
        self._manager.plan(target_jobs, forced_jobs)

        # Step 4:
        # Assign other config values.
        self._manager.configure(build_config)

    def run(self):
        self._manager.run(prev_config=self._explorer.get_base_config(),
                          prev_build_dir=self._explorer.get_base_build_dir(),
                          new_build_dir=self._explorer.make_new_build_dir())

    def print_jobs(self):
        self._manager.print_jobs()

    def print_config(self):
        self._manager.print_config()

    def _get_build_template(self, config):
        embedding_job = J.ComputeEmbeddings()

        if config['meta.language'] == 'en':
            return Builder.Build([
                J.DownloadPagesDump(config['meta.language']),
                J.DownloadLinksDump(config['meta.language']),
                J.DownloadCategoryLinksDump(config['meta.language']),
                J.DownloadPagePropertiesDump(config['meta.language']),
                J.DownloadRedirectsDump(config['meta.language']),
                J.DownloadEvaluationDatasets(),
                J.ImportPageTable(),
                J.ImportPagePropertiesTable(),
                J.ImportCategoryLinksTable(),
                J.ImportRedirectsTable(),
                J.CreateLinkEdgesTable(),
                J.ComputePagerank(),
                embedding_job,
                J.CreateTitleIndex(),
                J.EvaluateEmbeddings(),
                J.ComputeTSNE(),
                J.ComputeHighDimensionalNeighbors(),
                J.ComputeLowDimensionalNeighbors(),
                J.CreateAggregatedLinksTables(),
                J.CreateWikimapDatapointsTable(),
                J.CreateWikimapCategoriesTable(),
                J.CreateZoomIndex()])
        else:
            return Builder.Build([
                J.DownloadPagesDump(config['meta.language']),
                J.DownloadLinksDump(config['meta.language']),
                J.DownloadCategoryLinksDump(config['meta.language']),
                J.DownloadPagePropertiesDump(config['meta.language']),
                J.ImportPageTable(),
                J.ImportPagePropertiesTable(),
                J.ImportCategoryLinksTable(),
                J.CreateLinkEdgesTable(),
                J.ComputePagerank(),
                embedding_job,
                J.ComputeTSNE(),
                J.ComputeHighDimensionalNeighbors(),
                J.ComputeLowDimensionalNeighbors(),
                J.CreateAggregatedLinksTables(),
                J.CreateWikimapDatapointsTable(),
                J.CreateWikimapCategoriesTable(),
                J.CreateZoomIndex()])

    def _resolve_job_aliases(self, aliased_jobs, build_template):
        if aliased_jobs == ['_ALL_']:
            return [job.number for job in build_template]

        if aliased_jobs == ['_NONE_']:
            return []

        resolved_jobs = []
        for alias in aliased_jobs:
            for job in build_template:
                if job.alias == alias:
                    resolved_jobs.append(job.number)
                    break
            else:
                raise Utils.ParseException(
                    'Unrecognized alias: {}'.format(alias))

        return resolved_jobs
