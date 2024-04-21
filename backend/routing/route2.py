from logging import getLogger

from fastapi import APIRouter, Body, Request

from repos.repo2 import put_names_together

logger = getLogger()

router2 = APIRouter()


@router2.get("/item", tags=["route 2"])
def item(
    request: Request,
    payload: dict = Body(),
):
    logger.info("item")
    logger.info(f"Payload: {payload}")
    logger.info(f"request: {request}")


@router2.get("/names", tags=["route 2"])
def names(
    first_name: str,
    last_name: str,
    request: Request,
    payload: dict = Body(),
):
    logger.info("names")
    logger.info(f"Payload: {payload}")
    logger.info(f"first_name: {first_name}")
    logger.info(f"last_name: {last_name}")
    full_name = put_names_together(
        first_name=first_name,
        last_name=last_name,
    )
    logger.info("back in names")
    logger.info(f"full_name: {full_name}")
    logger.info(f"request: {request}")
