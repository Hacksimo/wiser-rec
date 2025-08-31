# app/routers/api.py   (or your api.py)
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import List, Union
from app.models import RecommendationRequest, RecommendationResponse, InteractionRequest, ResetResponse
# Ajusta el import si tu helper está en app.services.scoring o app.services.helpers
from app.services import mf                        # module that implements init_model/get_model/save_model
from app.services.helpers import compute_interaction_score  
from app.services.redis.redis_queue import interaction_queue
from app.services.redis.tasks import process_interaction
import json
from typing import List, Union
from fastapi import APIRouter, HTTPException

from app.services.redis.redis_queue import interaction_queue
from app.services.redis.redis_model import load_model, reset_model
from app.services.mf import MatrixFactorization

router = APIRouter()

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
    model = load_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    # you may want to fetch "seen" items from a store and pass exclude_seen
    recs = model.recommend(req.user_id, top_n=req.top_n)
    return RecommendationResponse(user_id=req.user_id,
                                  recommendations=[{"video_id": v, "score": s} for v, s in recs])

# --- endpoint: interact (synchronous update) ---
@router.post("/interact")
def interact_sync(payload: Union[InteractionRequest, List[InteractionRequest]]):
    """
    Synchronous: computes score and updates model within the request.
    Use this for low-throughput or when you want updates applied immediately.
    """

    
    
    interactions = payload if isinstance(payload, list) else [payload]
    
    job_ids = []
    for inter in interactions:
        job = interaction_queue.enqueue("app.services.redis.tasks.process_interaction", inter.model_dump())
        job_ids.append(job.id)

    return {"status": "queued", "jobs": job_ids}


@router.delete("/reset", response_model=ResetResponse)
def reset_model_endpoint():
    """
    Resets the stored model in Redis. The in-memory model remains unchanged.
    """
    reset_model()
    return ResetResponse(status="model reset in Redis")