from typing import Optional, Dict, Any
from datetime import datetime
from app.repositories.weather_repository import WeatherRepository
from app.utils.weather_client import WeatherAPIClient
import logging
import uuid

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self, repository: WeatherRepository, weather_client: WeatherAPIClient):
        self.repository = repository
        self.weather_client = weather_client

    async def get_weather(
            self,
            city_name: str,
            unit: str = "celsius",
            ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        cached_query = await self.repository.get_recent_cached_query(city_name)
        if cached_query:
            cached_data = cached_query.to_dict()
            cached_data.update({
                "served_from_cache": True,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow(),
                "id": cached_data.get("id", str(uuid.uuid4()))
            })
            return cached_data

        logger.info(f"Fetching fresh weather for {city_name}")
        weather_data = await self.weather_client.get_weather(city_name, unit)

        query_data = {
            **weather_data,
            "ip_address": ip_address,
            "served_from_cache": False,
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow()
        }

        new_query = await self.repository.create(query_data)
        return new_query.to_dict()

    async def get_query_history(
            self,
            city: Optional[str] = None,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            page: int = 1,
            per_page: int = 10
    ) -> Dict[str, Any]:
        queries = await self.repository.get_query_history(
            city=city,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page
        )

        total = await self.repository.get_total_count(
            city=city,
            date_from=date_from,
            date_to=date_to
        )

        return {
            "queries": [query.to_dict() for query in queries],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
