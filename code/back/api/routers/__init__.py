"""API routers."""

from routers.auth import router as auth_router
from routers.offices import router as offices_router
from routers.optimization import router as optimization_router
from routers.orders import router as orders_router
from routers.predictions import router as predictions_router
from routers.settings import router as settings_router

__all__ = [
    "auth_router",
    "offices_router",
    "orders_router",
    "optimization_router",
    "settings_router",
    "predictions_router",
]
