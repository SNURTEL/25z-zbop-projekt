from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_models import DayPrediction, DayPredictionV2, PredictionRequest, PredictionRequest2
from database import engine
from models import Base
from routers import (
    auth_router,
    offices_router,
    optimization_router,
    orders_router,
    predictions_router,
    settings_router,
)
from solver import generate_mock_predictions, generate_predictions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Coffee Inventory Optimization API",
    description="API for coffee inventory planning and optimization using MILP solver",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(offices_router)
app.include_router(orders_router)
app.include_router(optimization_router)
app.include_router(settings_router)
app.include_router(predictions_router)  # Legacy endpoint


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Coffee Consumption Prediction API"}


@app.post("/create_predictions")
async def create_predictions(request: PredictionRequest) -> list[DayPrediction]:
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
        normal_workers_daily=request.normal_workers_daily,
    )

    return predictions


@app.post("/create_predictions_v2")
async def create_predictions_v2(request: PredictionRequest2) -> list[DayPredictionV2]:
    predictions = generate_predictions(request)
    return predictions


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
