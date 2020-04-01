import logging
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).absolute().parents[1]))

from conf.path import LOG_DIRECTORY

# ------------------------------------------------------------------------------------------
# Level       |       When it’s used
# ------------------------------------------------------------------------------------------
# DEBUG       | Detailed information, typically of interest only when diagnosing problems.
# INFO        | Confirmation that things are working as expected.
# WARNING     | An indication that something unexpected happened, or indicative of some problem in the near future
#             | (e.g. ‘disk space low’). The software is still working as expected.
# ERROR       | Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL    | A serious error, indicating that the program itself may be unable to continue running.
# ------------------------------------------------------------------------------------------


class Logger:

    log_file = "file.log"

    @staticmethod
    def create(name="", steamhandler="stdout", log_file=None):
        if log_file is not None:
            if not Path(log_file).parent.is_dir():
                Path(log_file).parent.mkdir()
            Logger.log_file = log_file
        # create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # create console and file handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        fh = logging.FileHandler(Logger.log_file, mode='a', encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: (%(name)s) %(message)s')

        # add formatter to handlers
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger


if __name__ == "__main__":
    # logging.basicConfig(filename="file.log", format='%(asctime)s %(message)s', datefmt='%m/%d/%Y -> %I:%M:%S %p')
    logger = Logger().create(name=__name__)

    # 'application' code
    logger.debug('test debug message')
    logger.info('info message')
    logger.warning('test warn message')
    logger.error('error message')
    logger.critical('critical message')
