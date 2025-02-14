import logging

from app.backend.utilities import logger


from fastapi import FastAPI
from app.backend.routes.User import router as user_router
try:
    logging.info("Starting app...")
    app = FastAPI()
    logging.info("App started")
    logging.info("Including routers...")
    app.include_router(user_router)
    logging.info("Router added successfully")
except Exception as e:
    logging.error("Exception occured", exc_info=e)

