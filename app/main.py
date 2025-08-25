# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services import mf    # your services/mf module (contains init_model/get_model/save_model)
from app.routers import api    # your router(s)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: called once when the app starts
    # initialize or load the model
    mf.init_model(k=32, lr=0.01, reg=0.02, seed=1)
    # optionally expose model on app.state (not required if you use mf.get_model())
    app.state.model = mf.get_model()
    try:
        yield
    finally:
        # SHUTDOWN: called once when the app stops
        mf.save_model()

app = FastAPI(title="Recommendation Service", lifespan=lifespan)
app.include_router(api.router)