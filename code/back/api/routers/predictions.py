"""Legacy predictions endpoint for backward compatibility."""

from fastapi import APIRouter

from api_models import DayPredictionV2, PredictionRequest2
from solver import generate_predictions

router = APIRouter(tags=["Legacy Predictions"])


@router.post(
    "/create_predictions_v2",
    response_model=list[DayPredictionV2],
    summary="Create predictions (legacy)",
    description="Legacy endpoint for creating predictions. Use /optimization/requests for new integrations.",
)
def create_predictions_v2(request: PredictionRequest2) -> list[DayPredictionV2]:
    """
    Legacy prediction endpoint.
    
    This endpoint is maintained for backward compatibility.
    New integrations should use the /optimization/requests endpoint.
    """
    return generate_predictions(request)
