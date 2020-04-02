import logging
from pathlib import Path
import sys
import os
sys.path.append(str(Path(__file__).absolute().parents[1]))

from conf.cluster_conf import ENV_VAR_FOR_AWS_USER_ID, ENV_VAR_FOR_AWS_USER_KEY, ENV_VAR_FOR_ES_USER_ID, ENV_VAR_FOR_ES_USER_KEY

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
    main_fct = ""
    try:
        es_user = os.environ[ENV_VAR_FOR_ES_USER_ID]
        es_pwd = os.environ[ENV_VAR_FOR_ES_USER_KEY]
    except KeyError:
        es_user = None
        es_pwd = None
    try:
        s3_user = os.environ[ENV_VAR_FOR_AWS_USER_ID]
        s3_pwd = os.environ[ENV_VAR_FOR_AWS_USER_KEY]
    except KeyError:
        s3_user = None
        s3_pwd = None

    @staticmethod
    def create(logger_name="", streamhandler=sys.stdout, log_file=None, main_fct=None):
        if log_file is not None:
            if not Path(log_file).parent.is_dir():
                Path(log_file).parent.mkdir()
            Logger.log_file = log_file
        if main_fct is not None:
            Logger.main_fct = main_fct
        # create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        # create console and file handler
        ch = logging.StreamHandler(stream=streamhandler)
        ch.setLevel(logging.DEBUG)
        fh = logging.FileHandler(Logger.log_file, mode='a', encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        # create formatter
        console_formatter = logging.Formatter(f'%(asctime)s [%(levelname)8s]: (%(name)s) %(message)s',
                                              datefmt='%Y-%m-%d %H:%M:%S')
        file_formatter = logging.Formatter(f'%(asctime)s [%(levelname)8s]: '
                                           f'({Logger.main_fct} | {Logger.es_user}) (%(name)s) %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S')

        # add formatter to handlers
        ch.setFormatter(console_formatter)
        fh.setFormatter(file_formatter)

        # add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger


if __name__ == "__main__":
    # logging.basicConfig(filename="file.log", format='%(asctime)s %(message)s', )
    logger = Logger().create(logger_name=__name__, main_fct=Path(__file__).name)

    # 'application' code
    logger.debug('test debug message')
    logger.info('info message')
    logger.warning('test warn message')
    logger.error('error message')
    logger.critical('critical message')
