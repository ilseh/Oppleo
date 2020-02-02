import logging
import sys


def init_log(process_name, log_file):
    logger_daemon = logging.getLogger(process_name)
    logger_package = logging.getLogger('nl.carcharging')
    logger_package.setLevel(logging.DEBUG)
    logger_daemon.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(process)d %(processName)s - %(thread)d %(threadName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger_package.addHandler(fh)
    logger_daemon.addHandler(fh)
    logger_package.addHandler(ch)
    logger_daemon.addHandler(ch)

    # Redirect stdout to logfile
    log_file = open(log_file, "a")

    sys.stdout = log_file
