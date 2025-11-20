from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TemperatureUnit(str, Enum):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"

class WeatherQueryCreate(BaseModel):
    city_name: str = Field(..., min_length=1, max_length=100)
    unit: TemperatureUnit = TemperatureUnit.CELSIUS

class WeatherResponse(BaseModel):
    id: str
    city_name: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    weather_description: str
    weather_main: str
    wind_speed: float
    unit: TemperatureUnit
    served_from_cache: bool
    timestamp: datetime

class WeatherQueryFilter(BaseModel):
    city: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

class PaginatedResponse(BaseModel):
    queries: List[WeatherResponse]
    total: int
    page: int
    per_page: int
    total_pages: int