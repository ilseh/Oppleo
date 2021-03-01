import logging
import sys
import os

def init_log(process_name, log_file, daemons=[]):
    logger_process = logging.getLogger(process_name)
    logger_package = logging.getLogger('nl.oppleo')
    logger_process.setLevel(logging.DEBUG)
    logger_package.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    try:
        fh = logging.FileHandler(log_file)
    except PermissionError as pe:
        # So this location is  not allowed. Fall back to the Oppleo directory
        log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)).split('src/nl/oppleo/config')[0], 'Oppleo.log')
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
    logger_process.addHandler(fh)
    logger_process.addHandler(ch)
    logger_package.addHandler(fh)
    logger_package.addHandler(ch)

    for daemon in daemons:
        logger_daemon = logging.getLogger(daemon)
        logger_daemon.setLevel(logging.DEBUG)
        logger_daemon.addHandler(fh)
        logger_daemon.addHandler(ch)

    # Redirect stdout to logfile
    log_file = open(log_file, "a")

    # sys.stdout = log_file
