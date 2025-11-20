"""API route modules"""
from .weather import router as weather_router
from .health import router as health_router

__all__ = ["weather_router", "health_router"]