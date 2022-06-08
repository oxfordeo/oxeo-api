from fastapi import FastAPI
from mangum import Mangum

from oxeo.api import routes

app = FastAPI()
app.include_router(routes.router)

handler = Mangum(app=app)
