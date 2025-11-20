import aiohttp
from typing import Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class WeatherAPIClient:
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_URL

    async def get_weather(self, city_name: str, unit: str) -> Dict[str, Any]:
        params = {
            'q': city_name,
            'appid': self.api_key,
            'units': 'metric' if unit == 'celsius' else 'imperial'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._transform_weather_data(data, unit)
                else:
                    logger.error(f"Weather API error: {response.status}")
                    raise Exception(f"Failed to fetch weather: {response.status}")

    def _transform_weather_data(self, data: Dict[str, Any], unit: str) -> Dict[str, Any]:
        return {
            'city_name': data['name'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'weather_description': data['weather'][0]['description'],
            'weather_main': data['weather'][0]['main'],
            'wind_speed': data['wind']['speed'],
            'unit': unit
        }