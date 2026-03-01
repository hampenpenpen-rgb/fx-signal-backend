# main.py
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from fxdata import fetch_candles

app = FastAPI(title="fx-signal-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"ok": True, "docs": "/docs"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/candles")
async def candles(
    pair: str = Query("AUD/USD"),          # ← TwelveDataは "AUD/USD" 形式
    count: int = Query(200, ge=50, le=1000),
    interval: str = Query("1min"),
):
    return await fetch_candles(pair=pair, count=count, interval=interval)
