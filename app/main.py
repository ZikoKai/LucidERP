import os
from secrets import compare_digest

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.master_data import router as master_router


def require_key(x_api_key: str | None = Header(default=None)):
    key = os.getenv("API_KEY")
    if key and not compare_digest(x_api_key or "", key):
        raise HTTPException(401, "Invalid or missing X-API-Key")


app = FastAPI(title="LucidERP", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(master_router, dependencies=[Depends(require_key)])


@app.get("/health")
def health():
    return {"status": "ok"}
