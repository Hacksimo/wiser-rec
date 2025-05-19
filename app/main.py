from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Video Recommendation API")
app.include_router(router)