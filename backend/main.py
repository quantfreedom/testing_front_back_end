import uvicorn
from mangum import Mangum
from logging import getLogger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from custom_logger import set_loggers
from routing.route1 import router1
from routing.route2 import router2

set_loggers()
logger = getLogger()

app = FastAPI()

logger.info("Server started")
app.include_router(router1)
app.include_router(router2)

logger.info("Origins set")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app)
logger.info("Handler set")
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=5000,
    )
