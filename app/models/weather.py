from sqlalchemy import Column, String, DateTime, Float, Boolean, Integer
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class WeatherQuery(Base):
    __tablename__ = "weather_queries"

    id = Column(String, primary_key=True, default=generate_uuid)
    city_name = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    temperature = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Integer)
    pressure = Column(Integer)
    weather_description = Column(String)
    weather_main = Column(String)
    wind_speed = Column(Float)
    unit = Column(String, default="celsius")
    served_from_cache = Column(Boolean, default=False)
    ip_address = Column(String)

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