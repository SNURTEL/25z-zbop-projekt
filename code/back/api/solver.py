from typing import Dict, List
import random

from fastapi import logger


def generate_mock_predictions(max_capacity: int, conferences_per_week: int, normal_workers_daily: int) -> List[Dict]:
    """
    Mock function to generate coffee consumption predictions for 7 days.
    This should be replaced with actual prediction logic later.
    """
    predictions = []
    cumulative_remaining = max_capacity
    
    # Basic mock logic - adjust consumption based on parameters
    base_consumption_per_worker = 25  # grams per worker per day
    conference_multiplier = 1.5 if conferences_per_week > 3 else 1.2
    
    for day in range(1, 8):  # 7 days
        # Mock daily consumption calculation
        daily_consumption = int(normal_workers_daily * base_consumption_per_worker)
        
        # Add some randomness and conference effect
        if day <= conferences_per_week:
            daily_consumption = int(daily_consumption * conference_multiplier)
        
        # Add some random variation (±20%)
        variation = random.uniform(0.8, 1.2)
        daily_consumption = int(daily_consumption * variation)
        
        # Mock order amount (refill when running low)
        order_amount = 0
        if cumulative_remaining < max_capacity * 0.3:  # Refill when below 30%
            order_amount = max_capacity
            cumulative_remaining += order_amount
        
        # Calculate remaining amount
        cumulative_remaining = max(0, cumulative_remaining - daily_consumption)
        
        predictions.append({
            "day": day,
            "orderAmount": order_amount,
            "consumedAmount": daily_consumption,
            "remainingAmount": cumulative_remaining,
            "unit": "grams"
        })
    
    logger.logger.info("Generated mock predictions: %s", predictions)
    
    return predictions