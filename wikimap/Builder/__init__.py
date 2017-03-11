from Planner import BuildPlanner
from Explorer import build_explorer
from Manager import BuildManager
import sys

def set_builds_dir(builds_dir, build_prefix):
    build_explorer.set_builds_dir(builds_dir, build_prefix)

def get_build_plan(build, target_jobs, forced_jobs):
    planner = BuildPlanner(build)
    return planner.get_plan(target_jobs, forced_jobs)

def run_build(build, plan):
    manager = BuildManager(build, plan)
    try:
        manager.run()
    except Exception, _:
        sys.exit(1)
