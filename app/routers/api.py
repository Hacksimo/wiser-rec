# app/routers/api.py   (or your api.py)
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import List, Union
from app.models import RecommendationRequest, RecommendationResponse, InteractionRequest
# Ajusta el import si tu helper está en app.services.scoring o app.services.helpers
from app.services import mf                        # module that implements init_model/get_model/save_model
from app.services.helpers import compute_interaction_score  

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
    model = mf.get_model()
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

    

    model = mf.get_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    
    interactions = payload if isinstance(payload, list) else [payload]

    results = []
    for inter in interactions:
        score = compute_interaction_score(
            like=inter.like,
            watchtime=inter.watchtime or 0.0,
            duration=inter.duration,
            dont_suggest=inter.dont_suggest,
            comment=inter.comentario or ""
        )

        model.update(inter.user_id, inter.video_id, score)

        results.append({
            "user_id": inter.user_id,
            "video_id": inter.video_id,
            "score": float(score)
        })

    return {"status": "ok", "applied": len(results), "results": results}

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
