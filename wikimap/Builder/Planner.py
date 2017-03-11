from collections import defaultdict

class BuildPlanner(object):
    def __init__(self, build):
        self._build = build
        self._dep_graph = self._build_dependency_graph()

    def get_plan(self, target_jobs, forced_jobs):
        forced_jobs = set(forced_jobs)
        target_jobs = set(target_jobs) | forced_jobs

        jobs_count = len(self._build)

        included_jobs_mask = [job_num in target_jobs for job_num in range(jobs_count)]
        forced_jobs_mask = [job_num in forced_jobs for job_num in range(jobs_count)]

        for i in range(jobs_count-1, -1, -1):
            if included_jobs_mask[i]:
                for j in self._dep_graph[i]:
                    included_jobs_mask[j] = True

        return included_jobs_mask, forced_jobs_mask

    def _build_dependency_graph(self):
        graph = [[]]*len(self._build)
        deps = self._get_dependencies()
        for (dep_of, dep_on) in deps:
            graph[dep_of].append(dep_on)
        return graph

    def _get_dependencies(self):
        # A dependency exists between jobs if one's output is another's input and the second one is performed after the first.
        # The dependency is directed from the latter to the former.
        output_2_jobs = self._get_output_2_jobs()
        deps = set()
        for job_num, job in enumerate(self._build):
            inputs = job.inputs()
            for i in inputs:
                job_nums = output_2_jobs[i]
                for j in job_nums:
                    if j < job_num:
                        deps.add((job_num, j))
        return deps

    def _get_output_2_jobs(self):
        output_2_jobs = defaultdict(list) # numbers of jobs that have the key as an output
        for job_num, job in enumerate(self._build):
            outputs = job.outputs()
            for o in outputs:
                output_2_jobs[o].append(job_num)
        return output_2_jobs
