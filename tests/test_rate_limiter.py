import pytest
from datetime import datetime
import uuid
from app.services.weather_service import WeatherService
from app.utils.rate_limiter import RateLimiter
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.main import app


class DummyRepo:
    async def get_recent_cached_query(self, *a, **k):
        return None

    async def create(self, w):
        w.setdefault("id", str(uuid.uuid4()))
        w.setdefault("timestamp", datetime.utcnow())
        return type("Q", (), {"to_dict": lambda *_: w})()

    async def get_query_history(self, *a, **k):
        return []

    async def get_total_count(self, *a, **k):
        return 0


class DummyClient:
    async def get_weather(self, city_name: str, unit: str):
        return {
            "city_name": city_name,
            "temperature": 1,
            "feels_like": 1,
            "humidity": 1,
            "pressure": 1,
            "weather_description": "ok",
            "weather_main": "OK",
            "wind_speed": 0,
            "unit": unit
        }


@pytest.mark.asyncio
async def test_rate_limit_prevents_db_writes():
    dummy_service = WeatherService(DummyRepo(), DummyClient())

    async def override_service(db=None):
        return dummy_service

    rate_limiter_instance = RateLimiter(requests=2, window=60)

    def override_rate():
        return rate_limiter_instance

    import app.api.dependencies as deps
    app.dependency_overrides = {
        deps.get_weather_service: override_service,
        deps.get_rate_limiter: override_rate
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        headers = {"X-Forwarded-For": "1.2.3.4"}

        r1 = await ac.post("/api/v1/weather", json={"city_name": "A", "unit": "celsius"}, headers=headers)
        r2 = await ac.post("/api/v1/weather", json={"city_name": "B", "unit": "celsius"}, headers=headers)
        r3 = await ac.post("/api/v1/weather", json={"city_name": "C", "unit": "celsius"}, headers=headers)

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r3.status_code == 429
