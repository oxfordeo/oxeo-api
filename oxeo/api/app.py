from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger
from mangum import Mangum

from oxeo.api import routes
from oxeo.api.description import description

tags_metadata = [
    {
        "name": "Authorisation",
        "description": "Authorisation routes manage user data.",
    },
    {
        "name": "AOIs",
        "description": "Areas-of-interest with polygonal geometries and properties.",
    },
    {
        "name": "Events",
        "description": "Timestamped key-value records associated with an AOI.",
    },
    {
        "name": "Assets",
        "description": "Real fixed-capital assets with point geometries.",
    },
    {
        "name": "Companies",
        "description": "Ultimate owners of assets.",
    },
]

app = FastAPI(
    title="Oxford Earth Observation - API",
    description=description,
    openapi_tags=tags_metadata,
)
app.include_router(routes.router)


@app.exception_handler(404)
async def custom_404_handler(_, __):
    logger.info("REDIRECT")
    return RedirectResponse("/docs")


handler = Mangum(app=app)
