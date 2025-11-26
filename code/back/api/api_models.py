from pydantic import BaseModel, model_validator, NonNegativeFloat, PositiveInt, NonNegativeInt

class PredictionRequest(BaseModel):
    max_capacity: int  # Maximum capacity of coffee magazine in grams
    conferences_per_week: int  # Number of conferences per week
    normal_workers_daily: int  # Number of normal workers daily

class PredictionRequest2(BaseModel):
    storage_capacity_kg: PositiveInt
    purchase_costs_pln_per_kg_daily: list[NonNegativeFloat]
    transport_cost_pln: NonNegativeFloat
    num_conferences_daily: list[NonNegativeInt]
    num_workers_daily: list[NonNegativeInt]
    initial_inventory_kg: NonNegativeFloat
    daily_loss_fraction: NonNegativeFloat
    planning_horizon_days: PositiveInt

    @model_validator(mode='after')
    def check_lengths_match_planning_horizon(self):
        assert len(self.purchase_costs_pln_per_kg_daily) == self.planning_horizon_days == len(self.num_conferences_daily) == len(self.num_workers_daily), \
            "Length of purchase_costs, num_conferences_daily, and num_workers_daily must match planning_horizon"
        
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "storage_capacity_kg": 150.0,
                    "purchase_costs_pln_per_kg_daily": [12.0, 10.0, 14.0, 10.0, 13.0, 11.0, 15.0],
                    "transport_cost_pln": 100.0,
                    "num_conferences_daily": [
                        1, 0, 3, 7, 0, 0, 0
                    ],
                    "num_workers_daily": [
                        50, 90, 60, 50, 31, 15, 15
                    ],
                    "initial_inventory_kg": 40.0,
                    "daily_loss_fraction": 0.1,
                    "planning_horizon_days": 7
                }
            ]
        }
    }

class DayPrediction(BaseModel):
    day: int
    orderAmount: int
    consumedAmount: int
    remainingAmount: int
    unit: str

class DayPredictionV2(BaseModel):
    day: int
    orderAmount: float
    consumedAmount: float
    remainingAmount: float
    unit: str
