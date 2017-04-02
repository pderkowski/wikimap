#!/usr/bin/env python

import argparse
from wikimap import Utils, Report, ReportConfig

def main():
    logger = Utils.get_logger(__name__)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('config', type=argparse.FileType('r'),
        help="Specify a configuration file.")
    args = parser.parse_args()

    try:
        report = Report(ReportConfig.from_string(args.config.read()))
        report.create()
    except Exception, e:
        logger.exception(e)
        raise

if __name__ == '__main__':
    Utils.config_logging(log_length="minimal")
    main()
