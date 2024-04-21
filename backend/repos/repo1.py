from logging import getLogger

logger = getLogger()


def do_adding(
    number: int,
):
    logger.info("do_adding")
    logger.info(f"number: {number} + 5 = {number + 5}")
    result = number + 5
    return result
