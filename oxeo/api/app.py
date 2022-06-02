import os

from fastapi import FastAPI

from oxeo.api import routes

SECRET = os.environ.get("SERVER-SECRET", "my-secret")

# a quick create-all
# database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(routes.router)
