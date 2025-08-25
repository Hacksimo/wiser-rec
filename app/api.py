# app/routers/api.py   (or your api.py)
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Ajusta el import si tu helper está en app.services.scoring o app.services.helpers
from app.services import mf                        # module that implements init_model/get_model/save_model
from app.services.helpers import compute_interaction_score  

router = APIRouter()

# --- request models ---
class RecommendationRequest(BaseModel):
    user_id: int
    top_n: Optional[int] = 10

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: list

class InteractionRequest(BaseModel):
    user_id: int
    video_id: int
    like: Optional[int] = 0
    comentario: Optional[str] = ""
    watchtime: Optional[float] = 0.0
    duration: Optional[float] = None         # optional: helps compute watch ratio
    dont_suggest: Optional[int] = 0
    timestamp: Optional[datetime] = None
    user_meta: Optional[Dict[str, Any]] = None   # optional metadata for warm-start
    video_meta: Optional[Dict[str, Any]] = None

# --- internal helper to process interaction (safe to call in background) ---
def _process_interaction(payload: dict):
    """
    payload: dict from InteractionRequest.dict()
    This function computes the score and calls model.update(...)
    Keep this synchronous and fast (no DB/blocking calls). If heavy IO is required,
    run it in a worker process.
    """
    # compute score - uses your scoring helper
    score = compute_interaction_score(
        like=payload.get("like", 0),
        watchtime=payload.get("watchtime", 0.0),
        duration=payload.get("duration"),
        dont_suggest=payload.get("dont_suggest", 0),
        comment=payload.get("comentario", "")
    )

    model = mf.get_model()   # module-level singleton
    # If your MatrixFactorization implements warm-start using metadata, pass it here.
    # Example: model.update(user_id, video_id, score, user_meta=..., video_meta=...)
    # Our simple update signature: update(user_id, video_id, rating)
    model.update(payload["user_id"], payload["video_id"], score)

    # Optionally: return something or log (do not rely on return in background tasks)
    return {"updated": True, "score": float(score)}

# --- endpoint: get recommendations (example) ---
@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(req: RecommendationRequest, request: Request):
    # model can be retrieved via mf.get_model() or from app.state if you stored it there
    model = mf.get_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    # you may want to fetch "seen" items from a store and pass exclude_seen
    recs = model.recommend(req.user_id, top_n=req.top_n)
    return RecommendationResponse(user_id=req.user_id,
                                  recommendations=[{"video_id": v, "score": s} for v, s in recs])

# --- endpoint: interact (synchronous update) ---
@router.post("/interact")
def interact_sync(payload: InteractionRequest):
    """
    Synchronous: computes score and updates model within the request.
    Use this for low-throughput or when you want updates applied immediately.
    """
    # compute score
    score = compute_interaction_score(
        like=payload.like,
        watchtime=payload.watchtime or 0.0,
        duration=payload.duration,
        dont_suggest=payload.dont_suggest,
        comment=payload.comentario or ""
    )

    model = mf.get_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")

    # update (this must be thread-safe inside model)
    model.update(payload.user_id, payload.video_id, score)

    return {"status": "ok", "applied": True, "score": float(score)}

# --- endpoint: interact (background update) - RECOMMENDED for production ---
@router.post("/interact_bg")
def interact_background(payload: InteractionRequest, background_tasks: BackgroundTasks):
    """
    Fast response: the interaction is enqueued into FastAPI BackgroundTasks
    and processed asynchronously (still inside this process).
    For higher scale, replace BackgroundTasks by a queue (Redis/Celery/RQ).
    """
    background_tasks.add_task(_process_interaction, payload.dict())
    # reply immediately
    return {"status": "accepted", "applied": False}
