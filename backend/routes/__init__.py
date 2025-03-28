from fastapi import APIRouter
from .build_predictions import router as build_predictions_router
from .system_metrics import router as system_metrics_router
from .dashboard import router as dashboard_router
from .settings import router as settings_router
from .visualization import router as visualization_router

# Create main router
api_router = APIRouter()

# Include all routers
api_router.include_router(build_predictions_router)
api_router.include_router(system_metrics_router)
api_router.include_router(dashboard_router)
api_router.include_router(settings_router)
api_router.include_router(visualization_router)

__all__ = ['api_router']
