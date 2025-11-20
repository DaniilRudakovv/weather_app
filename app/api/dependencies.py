from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database.session import get_db
from app.repositories.weather_repository import WeatherRepository
from app.services.weather_service import WeatherService
from app.utils.weather_client import WeatherAPIClient
from fastapi import Request, HTTPException, Depends
from app.utils.rate_limiter import RateLimiter

limiter = Limiter(key_func=get_remote_address)

async def get_weather_service(db: AsyncSession = Depends(get_db)) -> WeatherService:
    repository = WeatherRepository(db)
    weather_client = WeatherAPIClient()
    return WeatherService(repository, weather_client)

def get_client_ip(request: Request) -> str:
    return get_remote_address(request)



def get_rate_limiter():
    return RateLimiter(requests=5, window=60)  # дефолт


async def rate_limit(
    request: Request,
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    ip = request.client.host

    if not limiter.is_allowed(ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")
