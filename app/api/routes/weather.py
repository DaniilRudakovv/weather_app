from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
import csv
import io
from typing import Optional
from datetime import datetime

from app.schemas.weather import (
    WeatherQueryCreate,
    WeatherResponse,
    PaginatedResponse
)
from app.api.dependencies import get_weather_service, get_client_ip, limiter, get_rate_limiter
from app.services.weather_service import WeatherService
from app.utils.rate_limiter import RateLimiter

router = APIRouter()


@router.post("/weather", response_model=WeatherResponse)
async def get_weather(
        request: Request,
        query: WeatherQueryCreate,
        weather_service: WeatherService = Depends(get_weather_service),
        rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    ip_address = get_client_ip(request)

    if not rate_limiter.is_allowed(ip_address):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )

    try:
        return await weather_service.get_weather(
            city_name=query.city_name,
            unit=query.unit,
            ip_address=ip_address
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching weather: {str(e)}"
        )


@router.get("/history", response_model=PaginatedResponse)
async def get_query_history(
        city: Optional[str] = Query(None),
        date_from: Optional[datetime] = Query(None),
        date_to: Optional[datetime] = Query(None),
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=100),
        weather_service: WeatherService = Depends(get_weather_service)
):
    return await weather_service.get_query_history(
        city=city,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page
    )


@router.get("/export")
async def export_history(
        city: Optional[str] = Query(None),
        date_from: Optional[datetime] = Query(None),
        date_to: Optional[datetime] = Query(None),
        weather_service: WeatherService = Depends(get_weather_service)
):
    data = await weather_service.get_query_history(
        city=city,
        date_from=date_from,
        date_to=date_to,
        page=1,
        per_page=10000
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'City', 'Temperature', 'Feels Like', 'Humidity',
        'Pressure', 'Description', 'Wind Speed', 'Unit',
        'Served From Cache', 'Timestamp'
    ])

    for query in data['queries']:
        writer.writerow([
            query['city_name'],
            query['temperature'],
            query['feels_like'],
            query['humidity'],
            query['pressure'],
            query['weather_description'],
            query['wind_speed'],
            query['unit'],
            query['served_from_cache'],
            query['timestamp']
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather_history.csv"}
    )