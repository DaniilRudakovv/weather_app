import pytest
from datetime import datetime, timedelta
import uuid
from app.services.weather_service import WeatherService
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.main import app

class MockQuery:
    def __init__(self, data):
        self.__dict__.update(data)

    def to_dict(self):
        return self.__dict__

class MockRepository:
    def __init__(self, recent=None):
        self._recent = recent
        self.created = []

    async def get_recent_cached_query(self, city_name: str, minutes: int = 5):
        return self._recent

    async def create(self, weather_data: dict):
        weather_data.setdefault("id", str(uuid.uuid4()))
        weather_data.setdefault("timestamp", datetime.utcnow())
        self.created.append(weather_data.copy())
        return MockQuery(weather_data)

    async def get_query_history(self, *args, **kwargs):
        return []

    async def get_total_count(self, *args, **kwargs):
        return 0

class MockWeatherClient:
    async def get_weather(self, city_name: str, unit: str):
        return {
            'city_name': city_name,
            'temperature': 20,
            'feels_like': 19,
            'humidity': 60,
            'pressure': 1000,
            'weather_description': 'cloudy',
            'weather_main': 'Clouds',
            'wind_speed': 3,
            'unit': unit
        }

@pytest.mark.asyncio
async def test_cache_reuse_and_fresh_fetch():
    recent_query = MockQuery({
        "city_name": "TestCity",
        "temperature": 15.0,
        "feels_like": 14.0,
        "humidity": 40,
        "pressure": 1005,
        "weather_description": "sunny",
        "weather_main": "Clear",
        "wind_speed": 2.0,
        "unit": "celsius",
        "served_from_cache": False,
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow() - timedelta(minutes=1)
    })

    repo_with_cache = MockRepository(recent=recent_query)
    weather_client = MockWeatherClient()
    service = WeatherService(repo_with_cache, weather_client)

    async def override_service(db=None):
        return service

    import app.api.dependencies as deps
    app.dependency_overrides = {deps.get_weather_service: override_service}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/weather", json={"city_name": "TestCity", "unit": "celsius"})
        data = resp.json()
        assert resp.status_code == 200
        assert data["served_from_cache"] is True
        assert data["city_name"] == "TestCity"
