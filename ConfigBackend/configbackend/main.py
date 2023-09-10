from fastapi import FastAPI

from configbackend.core.settings import get_settings


app = FastAPI(
    title="Config Backend",
    description="Config Backend",
    docs_url="/docs" if get_settings().enable_swagger else None,
    redoc_url=None,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
