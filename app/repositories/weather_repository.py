from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.weather import WeatherQuery


class WeatherRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, weather_data: dict) -> WeatherQuery:
        query = WeatherQuery(**weather_data)
        self.db.add(query)
        await self.db.commit()
        await self.db.refresh(query)
        return query

    async def get_recent_cached_query(self, city_name: str, minutes: int = 5) -> Optional[WeatherQuery]:
        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
        result = await self.db.execute(
            select(WeatherQuery)
            .where(
                and_(
                    WeatherQuery.city_name == city_name,
                    WeatherQuery.timestamp >= time_threshold,
                    WeatherQuery.served_from_cache == False
                )
            )
            .order_by(WeatherQuery.timestamp.desc())
        )
        return result.scalar_one_or_none()

    async def get_query_history(
            self,
            city: Optional[str] = None,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None,
            page: int = 1,
            per_page: int = 10
    ) -> List[WeatherQuery]:
        query = select(WeatherQuery)

        if city:
            query = query.where(WeatherQuery.city_name.ilike(f"%{city}%"))

        if date_from:
            query = query.where(WeatherQuery.timestamp >= date_from)

        if date_to:
            query = query.where(WeatherQuery.timestamp <= date_to)

        offset = (page - 1) * per_page
        query = query.order_by(WeatherQuery.timestamp.desc()).offset(offset).limit(per_page)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_total_count(
            self,
            city: Optional[str] = None,
            date_from: Optional[datetime] = None,
            date_to: Optional[datetime] = None
    ) -> int:
        query = select(func.count(WeatherQuery.id))

        if city:
            query = query.where(WeatherQuery.city_name.ilike(f"%{city}%"))

        if date_from:
            query = query.where(WeatherQuery.timestamp >= date_from)

        if date_to:
            query = query.where(WeatherQuery.timestamp <= date_to)

        result = await self.db.execute(query)
        return result.scalar_one()