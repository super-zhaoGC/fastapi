from fastapi import APIRouter
from app.core.logger import logger


home_router = APIRouter()

@home_router.get("/")
def home():
    logger.info("Hello World")
    return {"message": "Hello World"}