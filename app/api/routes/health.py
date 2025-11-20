from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import aiohttp
import asyncio
from app.database.session import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
        logger.info("Database health check passed")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {str(e)}")
    api_status = "unknown"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.openweathermap.org", timeout=5) as response:
                api_status = "healthy" if response.status == 200 else f"unhealthy: {response.status}"
                logger.info(f"External API health check: {api_status}")
    except asyncio.TimeoutError:
        api_status = "timeout"
        logger.warning("External API health check timeout")
    except Exception as e:
        api_status = f"unhealthy: {str(e)}"
        logger.error(f"External API health check failed: {str(e)}")

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "external_api": api_status
    }