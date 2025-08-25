from fastapi import APIRouter
from models import RecommendationRequest, RecommendationResponse
from services.mf import MatrixFactorization 

router = APIRouter()

@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendation(req: RecommendationRequest):
    return recommend(req.user_id)