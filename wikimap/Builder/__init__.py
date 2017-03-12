from Planner import BuildPlanner
from Explorer import build_explorer
from Manager import BuildManager
import sys
import logging

def set_builds_dir(builds_dir, build_prefix):
    build_explorer.set_builds_dir(builds_dir, build_prefix)

def set_base_build(build_index):
    logger = logging.getLogger(__name__)
    if not build_explorer.has_build_dir(build_index):
        logger.warning('Setting base build index to {}, but such build does not exist.'.format(build_index))
    build_explorer.set_base_build(build_index)

def run_build(build):
    manager = BuildManager(build)
    try:
        manager.run()
    except Exception, _:
        sys.exit(1)
