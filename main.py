from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import init_db, upsert_device, list_devices
from push_expo import send_expo_push

app = FastAPI()

class RegisterReq(BaseModel):
    device_id: str
    expo_token: str

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/devices/register")
def register(req: RegisterReq):
    upsert_device(req.device_id, req.expo_token)
    return {"ok": True}

@app.get("/devices")
def devices():
    return {"devices": list_devices()}

@app.post("/push/test")
async def push_test():
    devices = list_devices()
    if not devices:
        raise HTTPException(status_code=400, detail="no devices registered")
    d = devices[0]
    code, text = await send_expo_push(
        d["expo_token"],
        "TEST",
        "Hello from backend",
        {"kind":"TEST"}
    )
    return {"ok": True, "status": code, "resp": text}
