from logging import getLogger

logger = getLogger()


def put_names_together(
    first_name: str,
    last_name: str,
):
    logger.info("add_last_name")
    last_name = "Smith"
    first_plus_last = first_name + " " + last_name
    logger.info(f"first_name: {first_name} + last_name: {last_name} = {first_plus_last}")
    return first_plus_last
