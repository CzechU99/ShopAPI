# app/services/external_client.py
import requests
import logging
from typing import Optional

logger = logging.getLogger("app.external_client")

EXTERNAL_URL = "http://external_service:8001/external/data"  # nazwa usługi w docker-compose

def call_external_service(correlation_id: Optional[str] = None, timeout: int = 5):
    headers = {}
    if correlation_id:
        headers["X-Correlation-Id"] = correlation_id

    try:
        resp = requests.get(EXTERNAL_URL, headers=headers, timeout=timeout)
        resp.raise_for_status()
        logger.info(f"external_client: call success, status={resp.status_code}, correlation_id={correlation_id}")
        return resp.json()
    except Exception as e:
        logger.error(f"external_client: call failed, correlation_id={correlation_id}, error={e}")
        raise
