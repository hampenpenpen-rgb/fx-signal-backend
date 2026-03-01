import httpx
from typing import Dict, Any, Tuple

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

async def send_expo_push(expo_token: str, title: str, body: str, data: Dict[str, Any]) -> Tuple[int, str]:
    payload = {
        "to": expo_token,
        "sound": "default",
        "title": title,
        "body": body,
        "data": data
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(EXPO_PUSH_URL, json=payload)
    return r.status_code, r.text
