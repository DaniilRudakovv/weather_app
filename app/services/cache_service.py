from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class CacheService:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self._cache:
            cached_data = self._cache[key]
            if datetime.now() < cached_data['expires_at']:
                return cached_data['data']
            else:
                del self._cache[key]
        return None

    def set(self, key: str, data: Dict[str, Any], ttl: int = 300):
        self._cache[key] = {
            'data': data,
            'expires_at': datetime.now() + timedelta(seconds=ttl)
        }