"""API routes and endpoints"""
from .routes import weather_router, health_router
from .dependencies import get_weather_service, get_client_ip, limiter, get_rate_limiter

__all__ = [
    "weather_router",
    "health_router",
    "get_weather_service",
    "get_client_ip",
    "limiter",
    "get_rate_limiter"
]