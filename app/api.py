from fastapi import APIRouter
from app.models import RecommendationRequest, RecommendationResponse
from app.recommender import recommend

router = APIRouter()

@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(req: RecommendationRequest):
    return recommend(req.user_id)