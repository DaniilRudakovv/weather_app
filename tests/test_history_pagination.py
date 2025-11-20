import pytest
from datetime import datetime, timedelta

from app.services.weather_service import WeatherService

@pytest.mark.asyncio
async def test_get_query_history_pagination_and_total_pages():

    class DummyQuery:
        def __init__(self, i):
            self.id = f"id-{i}"
            self.city_name = f"City{i%3}"
            self.timestamp = datetime.utcnow() - timedelta(days=i)
            self.temperature = 1.0 * i
            self.feels_like = 1.0 * i
            self.humidity = 10
            self.pressure = 1000
            self.weather_description = "desc"
            self.weather_main = "Main"
            self.wind_speed = 1.0
            self.unit = "celsius"
            self.served_from_cache = False

        def to_dict(self):
            return {
                "id": self.id,
                "city_name": self.city_name,
                "timestamp": self.timestamp.isoformat(),
                "temperature": self.temperature,
                "feels_like": self.feels_like,
                "humidity": self.humidity,
                "pressure": self.pressure,
                "weather_description": self.weather_description,
                "weather_main": self.weather_main,
                "wind_speed": self.wind_speed,
                "unit": self.unit,
                "served_from_cache": self.served_from_cache
            }

    class DummyRepo:
        def __init__(self, total):
            self._total = total
        async def get_query_history(self, city=None, date_from=None, date_to=None, page=1, per_page=10):
            start = (page - 1) * per_page
            items = [DummyQuery(i) for i in range(start, min(start + per_page, self._total))]
            return items

        async def get_total_count(self, city=None, date_from=None, date_to=None):
            return self._total

    dummy_total = 25
    repo = DummyRepo(total=dummy_total)
    service = WeatherService(repo, weather_client=None)

    res = await service.get_query_history(city=None, date_from=None, date_to=None, page=2, per_page=10)
    assert res["page"] == 2
    assert res["per_page"] == 10
    assert res["total"] == dummy_total
    assert res["total_pages"] == (dummy_total + 10 - 1) // 10
    assert len(res["queries"]) <= 10
