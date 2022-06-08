import logging


def create_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    logger.addHandler(ch)
    return logger
