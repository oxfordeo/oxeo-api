import uvicorn

if __name__ == "__main__":
    uvicorn.run("oxeo.api.app:app", host="0.0.0.0", port=8081, reload=True)
