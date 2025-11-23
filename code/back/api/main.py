from fastapi import FastAPI
from typing import List
from api_models import PredictionRequest, DayPrediction
from solver import generate_mock_predictions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Coffee Consumption Prediction API",
    description="API for predicting daily coffee consumption based on capacity and usage parameters",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Coffee Consumption Prediction API"}

@app.post("/create_predictions", response_model=List[DayPrediction])
async def create_predictions(request: PredictionRequest):
    """
    Create coffee consumption predictions based on provided parameters.
    
    Args:
        request: PredictionRequest containing:
            - max_capacity: Maximum capacity of coffee magazine in grams
            - conferences_per_week: Number of conferences per week
            - normal_workers_daily: Number of normal workers daily
    
    Returns:
        List of daily predictions with consumption, orders, and remaining amounts
    """
    predictions = generate_mock_predictions(
        max_capacity=request.max_capacity,
        conferences_per_week=request.conferences_per_week,
        normal_workers_daily=request.normal_workers_daily
    )
    
    return predictions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
