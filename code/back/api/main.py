from fastapi import FastAPI, HTTPException
from typing import List
from api_models import PredictionRequest, DayPrediction
from model.model import solve
from fastapi.middleware.cors import CORSMiddleware
from fastapi import logger

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
    try:
        # Hard-coded coffee cost per kg for 7 days (can be adjusted later)
        purchase_costs = [10, 12, 11, 9, 13, 10, 11]
        logger.logger.info("Received prediction request: %s", request)
        
        # Calculate daily demand: employees * 0.1 kg + conferences * 0.3 kg
        # conferences_per_week is distributed across 7 days
        conferences_per_day = request.conferences_per_week / 7.0
        daily_demand = request.normal_workers_daily * 0.1 + conferences_per_day * 1
        daily_demands = [int(daily_demand)] * 7  # Same demand for all 7 days
        
        logger.logger.info("Daily demands: %s", daily_demands)
        
        # Convert max_capacity from grams to kg
        V_max = request.max_capacity
        logger.logger.info("V_max (kg): %s", V_max)
        
        # Solve the optimization problem
        result = solve(
            purchase_costs=purchase_costs,
            daily_demands=daily_demands,
            V_max=V_max,
            C=50.0,  # Transport cost in zł
            I_0=V_max * 0.2,  # Start with 20% of capacity
            alpha=0.1  # 10% daily loss
        )

        logger.logger.info("Optimization result: %s", result)
        
        if not result:
            raise HTTPException(status_code=500, detail="Could not solve optimization problem")
        
        # Convert results to API response format
        predictions = []
        for day in range(1, 8):
            idx = day - 1
            predictions.append(DayPrediction(
                day=day,
                orderAmount=int(result['orders'][idx] * 1000),  # Convert kg to grams
                consumedAmount=int(daily_demands[idx] * 1000),  # Convert kg to grams
                remainingAmount=int(result['inventory'][idx] * 1000),  # Convert kg to grams
                unit="grams"
            ))
        
        logger.logger.info("Returning predictions: %s", predictions)
        return predictions
    
    except Exception as e:
        logger.logger.error("Error in create_predictions: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
