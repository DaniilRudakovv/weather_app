from typing import Dict, List
import time


class RateLimiter:
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window
        self.requests_log: Dict[str, List[float]] = {}

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        if ip not in self.requests_log:
            self.requests_log[ip] = []

        # Удаляем старые запросы
        self.requests_log[ip] = [
            req_time for req_time in self.requests_log[ip]
            if now - req_time < self.window
        ]

        if len(self.requests_log[ip]) < self.requests:
            self.requests_log[ip].append(now)
            return True

        return False