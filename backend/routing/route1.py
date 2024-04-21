from logging import getLogger

from fastapi import APIRouter, Body, Request

from repos.repo1 import do_adding

logger = getLogger()

router1 = APIRouter()


@router1.get("/nothing", tags=["route 1"])
def nothing(
    request: Request,
    payload: dict = Body(),
):
    logger.info("nothing")
    logger.info(f"Payload: {payload}")
    logger.info(f"request: {request}")


@router1.get("/adder", tags=["route 1"])
def adder(
    number: int,
    request: Request,
    payload: dict = Body(),
):
    logger.info("adder")
    logger.info(f"Payload: {payload}")
    logger.info(f"number: {number}")
    result = do_adding(number=number)
    logger.info("back in adder")
    logger.info(f"result: {result}")
    logger.info(f"request: {request}")
