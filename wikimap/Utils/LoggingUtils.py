import logging
import os

logging.IMPORTANT = 25
logging.addLevelName(logging.IMPORTANT, "IMPORTANT")

def important(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(logging.IMPORTANT):
        self._log(logging.IMPORTANT, message, args, **kws)

logging.Logger.important = important

class SingleProcessFilter(logging.Filter):
    master_pid = None

    def filter(self, record):
        pid = os.getpid()
        return self.master_pid != None and pid == self.master_pid

def config_logging(only_important=False):
    level = logging.IMPORTANT if only_important else logging.INFO
    logging.basicConfig(format='\33[2K\r%(asctime)s:%(filename)s:%(lineno)d:%(message)s', datefmt='%H:%M:%S', level=level)
    SingleProcessFilter.master_pid = os.getpid()

def get_logger(name):
    logger = logging.getLogger(name)
    logger.addFilter(SingleProcessFilter())
    return logger
