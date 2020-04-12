import logging
from pathlib import Path
from datetime import datetime
import sys
import os
sys.path.append(str(Path(__file__).absolute().parents[1]))

from conf.cluster_conf import ENV_VAR_FOR_ES_USER_ID
from conf.path import LOG_DIRECTORY

# ------------------------------------------------------------------------------------------
# Level       |       When it’s used
# ------------------------------------------------------------------------------------------
# DEBUG       | Detailed information, typically of interest only when diagnosing problems.
# INFO        | Confirmation that things are working as expected.
# WARNING     | An indication that something unexpected happened, or indicative of some problem in the near future
#             | (e.g. ‘disk space low’). The software is still working as expected.
# ERROR       | Due to a more serious problem, the software has not been able to perform some function.
#             | i.e. : it's an error if the function return error value or error code (None, -1, ..etc)
# CRITICAL    | A serious error, indicating that the program itself may be unable to continue running.
# ------------------------------------------------------------------------------------------


class Logger:

    timestamp = datetime.now().strftime("%Y%m%dT%H-%M-%S-%f")
    log_file = Path(LOG_DIRECTORY, f'log_{timestamp}.log')
    if log_file is not None:
        if not Path(log_file).parent.is_dir():
            Path(log_file).parent.mkdir()
    try:
        es_user = os.environ[ENV_VAR_FOR_ES_USER_ID]
    except KeyError:
        es_user = None

    @staticmethod
    def get_path():
        return Logger.log_file

    @staticmethod
    def get_json():
        with Logger.log_file.open(mode='r', encoding='utf-8') as fp:
            log_data = fp.read()
        log = {
            "user": Logger.es_user,
            "timestamp": Logger.timestamp,
            "log_file": str(Logger.log_file.absolute()),
            "message": log_data
        }
        return log

    @staticmethod
    def upload_log(index, es_host_ip, es_host_port):
        from get_data.src import es_utils
        json_log = Logger().get_json()
        es_utils.upload_single_doc(json_log, index=index, host_ip=es_host_ip, port=es_host_port)

    @staticmethod
    def create(logger_name="", streamhandler=sys.stdout):
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
                                           f'({Logger.es_user}) (%(name)s) %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S')

        # add formatter to handlers
        ch.setFormatter(console_formatter)
        fh.setFormatter(file_formatter)

        # add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger


if __name__ == "__main__":
    logger = Logger().create(logger_name=__name__)

    # 'application' code
    logger.debug('test debug message')
    logger.info('info message')
    logger.warning('test warn message')
    logger.error('error message')
    logger.critical('critical message')
    log_json = Logger.get_json()
    print(log_json)
