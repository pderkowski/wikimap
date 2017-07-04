from collections import defaultdict
from Job import Properties
from Build import Build
from .. import Utils


class BuildPlanner(object):
    def __init__(self, jobs):
        self._jobs = jobs
        self._dep_graph = self._build_dependency_graph()

    def plan(self, target_job_aliases, forced_job_aliases,
             skipped_jobs_aliases):
        target_job_nums = set(self._resolve_job_aliases(target_job_aliases))
        forced_job_nums = set(self._resolve_job_aliases(forced_job_aliases))

        target_job_nums |= forced_job_nums

        build = Build([self._jobs[job]
                       for job in self._get_included_jobs(target_job_nums)])

        for alias in forced_job_aliases:
            build[alias].properties.append(Properties.Forced)

        for alias in skipped_jobs_aliases:
            if Properties.Forced in build[alias].properties:
                raise ValueError(("A job cannot be forced and skipped at the "
                                  "same time."))
            else:
                build[alias].properties.append(Properties.Skipped)

        return build

    def _get_included_jobs(self, target_jobs):
        included_jobs = []

        for target in target_jobs:
            if target not in included_jobs:
                self._include(target, included_jobs)

        return included_jobs

    def _include(self, job, included_jobs):
        for dep in self._dep_graph[job]:
            if dep not in included_jobs:
                self._include(dep, included_jobs)

        included_jobs.append(job)

    def _build_dependency_graph(self):
        graph = [[] for _ in range(len(self._jobs))]
        deps = self._get_dependencies()
        for (dep_of, dep_on) in deps:
            graph[dep_of].append(dep_on)
        return graph

    def _get_dependencies(self):
        # A dependency exists between jobs if one's output is another's input.
        # The dependency is directed from the latter to the former.
        output_2_jobs = self._get_output_2_jobs()
        deps = set()
        for job_num, job in enumerate(self._jobs):
            for i in job.inputs:
                job_nums = output_2_jobs[i]
                for j in job_nums:
                    if j != job_num:  # can't depend on oneself
                        deps.add((job_num, j))
        return deps

    def _get_output_2_jobs(self):
        output_2_jobs = defaultdict(list) # numbers of jobs that have the key as an output
        for job_num, job in enumerate(self._jobs):
            for o in job.outputs:
                output_2_jobs[o].append(job_num)
        return output_2_jobs

    def _resolve_job_aliases(self, aliases):
        resolved_jobs = []
        for alias in aliases:
            for i, job in enumerate(self._jobs):
                if job.alias == alias:
                    resolved_jobs.append(i)
                    break
            else:
                raise Utils.ParseException(
                    'Unrecognized alias: {}'.format(alias))

        return resolved_jobs
