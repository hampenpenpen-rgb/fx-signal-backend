# fxdata.py
import os
import time
import datetime as dt
import httpx

DATA_PROVIDER = os.getenv("DATA_PROVIDER", "twelvedata").lower()
TWELVE_KEY = os.getenv("TWELVEDATA_API_KEY", "")

_cache = {}   # key -> (ts, data)
CACHE_TTL_SEC = 20

def _cache_get(key: str):
    v = _cache.get(key)
    if not v:
        return None
    ts, data = v
    if time.time() - ts > CACHE_TTL_SEC:
        return None
    return data

def _cache_set(key: str, data):
    _cache[key] = (time.time(), data)

def _to_epoch_ms(s: str) -> int:
    # TwelveDataは "YYYY-mm-dd HH:MM:SS" が多い
    # まずUTC扱いで統一（あとで改善できる）
    d = dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
    return int(d.timestamp() * 1000)

async def fetch_candles(pair: str, count: int = 200, interval: str = "1min"):
    pair = pair.strip()
    cache_key = f"{DATA_PROVIDER}:{pair}:{count}:{interval}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    if DATA_PROVIDER != "twelvedata":
        raise RuntimeError(f"Unknown DATA_PROVIDER: {DATA_PROVIDER}")

    if not TWELVE_KEY:
        raise RuntimeError("TWELVEDATA_API_KEY is not set")

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": pair,          # 例: "AUD/USD"
        "interval": interval,    # "1min"
        "outputsize": str(count),
        "format": "JSON",
        "apikey": TWELVE_KEY,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        j = r.json()

    if "values" not in j:
        raise RuntimeError(f"TwelveData error: {j}")

    values = j["values"]  # newest first
    candles = []
    for v in reversed(values):  # oldest -> newest
        candles.append({
            "t": _to_epoch_ms(v["datetime"]),
            "o": float(v["open"]),
            "h": float(v["high"]),
            "l": float(v["low"]),
            "c": float(v["close"]),
        })

    out = {"pair": pair, "interval": interval, "candles": candles}
    _cache_set(cache_key, out)
    return out
