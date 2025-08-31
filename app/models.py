from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

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

class ResetResponse(BaseModel):
    status: str