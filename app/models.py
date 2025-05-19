from pydantic import BaseModel
from typing import List

class RecommendationRequest(BaseModel):
    user_id: int

class RecommendationResponse(BaseModel):
    user_id: int
    recommended_videos: List[int]