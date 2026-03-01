import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pywebpush import webpush, WebPushException

app = FastAPI(title="fx-signal-backend")

# CORS（PWA(GitHub Pages)から叩けるようにする）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 後で絞ればOK。まず動かす。
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 環境変数 =====
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:example@example.com")  # 自分のメールに変えてOK

# ===== メモリ保存（まず動かす。永続化は後） =====
# vendor_id -> subscription(dict)
SUBS = {}

@app.get("/")
def root():
    return {"ok": True, "docs": "/docs"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/webpush/vapid_public")
def vapid_public():
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(500, "VAPID_PUBLIC_KEY is not set")
    return {"vapid_public_key": VAPID_PUBLIC_KEY}

class SubscribeReq(BaseModel):
    vendor_id: str
    subscription: dict

@app.post("/webpush/subscribe")
def webpush_subscribe(req: SubscribeReq):
    if not req.vendor_id:
        raise HTTPException(400, "vendor_id required")
    # subscriptionの最低限の形だけ確認
    if "endpoint" not in req.subscription:
        raise HTTPException(400, "subscription.endpoint missing")
    SUBS[req.vendor_id] = req.subscription
    return {"ok": True, "vendor_id": req.vendor_id}

class PushTestReq(BaseModel):
    vendor_id: str
    title: str = "Test"
    body: str = "Hello from backend"
    url: str = "/"

@app.post("/webpush/test")
def webpush_test(req: PushTestReq):
    if req.vendor_id not in SUBS:
        raise HTTPException(404, "vendor_id not subscribed")
    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        raise HTTPException(500, "VAPID keys not set")
    sub = SUBS[req.vendor_id]

    payload = json.dumps({
        "title": req.title,
        "body": req.body,
        "url": req.url,
    })

    try:
        webpush(
            subscription_info=sub,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
        )
        return {"ok": True, "sent": 1}
    except WebPushException as e:
        raise HTTPException(500, f"WebPush failed: {repr(e)}")
