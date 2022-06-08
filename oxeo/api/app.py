from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger
from mangum import Mangum

from oxeo.api import routes

app = FastAPI()
app.include_router(routes.router)


@app.exception_handler(404)
async def custom_404_handler(_, __):
    logger.info("REDIRECT")
    return RedirectResponse("/docs")


handler = Mangum(app=app)
