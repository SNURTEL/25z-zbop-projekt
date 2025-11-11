from pydantic import BaseModel

class PredictionRequest(BaseModel):
    max_capacity: int  # Maximum capacity of coffee magazine in grams
    conferences_per_week: int  # Number of conferences per week
    normal_workers_daily: int  # Number of normal workers daily

class DayPrediction(BaseModel):
    day: int
    orderAmount: int
    consumedAmount: int
    remainingAmount: int
    unit: str