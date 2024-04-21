from datetime import datetime, timezone
import os, logging
from time import gmtime


def set_loggers():
    try:
        logging.Formatter.converter = gmtime

        current_dir = os.path.dirname(os.path.abspath(__file__))
        complete_path = os.path.join(current_dir, "logs")

        isExist = os.path.exists(complete_path)
        if not isExist:
            os.makedirs(complete_path)

        file_format = f'info_{datetime.now(tz=timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")}.log'
        filename = os.path.join(complete_path, file_format)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(create_logging_handler(filename=filename))
        logger.info("Testing info log")

    except:  # this is for the aws lambda function
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        log_handler = logger.handlers[0]
        log_format = "\n%(levelname)s - %(filename)s - %(funcName)s() - %(lineno)d - %(message)s"
        log_handler.setFormatter(logging.Formatter(fmt=log_format))

        pass


def create_logging_handler(filename: str):
    handler = None
    try:
        handler = logging.FileHandler(
            filename=filename,
            mode="w",
        )
        log_format = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s() - %(lineno)d - %(message)s"
        handler.setFormatter(logging.Formatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        raise Exception(f"Couldnt create logging handler. Desc=[{e}]")

    return handler
