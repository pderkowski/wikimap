#!/usr/bin/env python

import argparse
import os
from wikimap import Utils, ReportCreator

def get_config(args):
    config = Utils.Config.from_string(args.config.read())
    config.validate(
        required=[('name', str), ('dest_dir', str), ('indices', str), ('builds_dir', str), ('build_prefix', str)],
        optional=[('included_tests', list)]
    )
    config['dest_dir'] = os.path.realpath(config['dest_dir'])
    config['dest_path'] = os.path.join(config['dest_dir'], config['name'])
    config['indices'] = Utils.parse_int_range(config['indices'])
    return config

def main():
    logger = Utils.get_logger(__name__)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('config', type=argparse.FileType('r'),
        help="Specify a configuration file.")
    args = parser.parse_args()

    try:
        config = get_config(args)
        creator = ReportCreator(config['builds_dir'], config['build_prefix'])
        creator.create(config['indices'], config['dest_path'], included_tests=config['included_tests'])
    except Exception, e:
        logger.exception(e)
        raise

if __name__ == '__main__':
    Utils.config_logging()
    main()
