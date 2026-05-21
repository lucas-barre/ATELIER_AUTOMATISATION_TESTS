import time
import requests
from requests.exceptions import RequestException, Timeout

class APIClient:
    def __init__(self, base_url="https://api.frankfurter.app", timeout=3.0, max_retries=1):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    def request(self, method, endpoint, params=None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        attempts = 0
        max_attempts = 1 + self.max_retries
        
        last_exception = None
        start_time = time.perf_counter()
        
        while attempts < max_attempts:
            attempts += 1
            try:
                sub_start = time.perf_counter()
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    timeout=self.timeout
                )
                latency_ms = (time.perf_counter() - sub_start) * 1000
                
                # Check for rate limit 429 and retry if possible
                if response.status_code == 429 and attempts < max_attempts:
                    # Simple backoff delay
                    time.sleep(2)
                    continue
                
                # Content type check
                is_json = "application/json" in response.headers.get("Content-Type", "")
                json_data = None
                if is_json:
                    try:
                        json_data = response.json()
                    except ValueError:
                        pass
                
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "json": json_data,
                    "text": response.text,
                    "latency_ms": latency_ms,
                    "attempts": attempts,
                    "error": None
                }
                
            except Timeout as e:
                last_exception = f"Timeout ({self.timeout}s)"
                if attempts < max_attempts:
                    time.sleep(1)
                    continue
            except RequestException as e:
                last_exception = str(e)
                if attempts < max_attempts:
                    time.sleep(1)
                    continue
                    
        total_latency_ms = (time.perf_counter() - start_time) * 1000
        return {
            "status_code": None,
            "headers": {},
            "json": None,
            "text": None,
            "latency_ms": total_latency_ms,
            "attempts": attempts,
            "error": last_exception
        }
