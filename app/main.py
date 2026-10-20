import os
from secrets import compare_digest

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.agent import ActionRead, DecisionRequest, attach_order, claim_decision
from app.agent import router as agent_router
from app.core import get_db
from app.master_data import router as master_router
from app.sales import OrderCreate, create_order, invoice_router
from app.sales import router as sales_router


def require_key(x_api_key: str | None = Header(default=None)):
    key = os.getenv("API_KEY")
    if key and not compare_digest(x_api_key or "", key):
        raise HTTPException(401, "Invalid or missing X-API-Key")


app = FastAPI(title="LucidERP", version="0.1.0")


@app.middleware("http")
async def protect_all_routes(request: Request, call_next):
    if request.url.path != "/health":
        try:
            require_key(request.headers.get("X-API-Key"))
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return await call_next(request)


# Add CORS last so browser preflights are processed outside the key gate.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(master_router, dependencies=[Depends(require_key)])
app.include_router(sales_router, dependencies=[Depends(require_key)])
app.include_router(invoice_router, dependencies=[Depends(require_key)])
app.include_router(agent_router, dependencies=[Depends(require_key)])


@app.post(
    "/agent-actions/{action_id}/approve",
    response_model=ActionRead,
    dependencies=[Depends(require_key)],
)
def approve(action_id: int, data: DecisionRequest, db: Session = Depends(get_db)):
    # Composition root owns the human-authorized transaction, outside the agent module.
    try:
        action = claim_decision(db, action_id, "approuvee", data.decide_par)
        order_data = OrderCreate.model_validate({**action.payload, "statut": "validee"})
        order = create_order(db, order_data)
        attach_order(action, order.id)
        db.commit()
        db.refresh(action)
        return action
    except Exception:
        db.rollback()
        raise


@app.post(
    "/agent-actions/{action_id}/reject",
    response_model=ActionRead,
    dependencies=[Depends(require_key)],
)
def reject(action_id: int, data: DecisionRequest, db: Session = Depends(get_db)):
    action = claim_decision(db, action_id, "rejetee", data.decide_par)
    db.commit()
    db.refresh(action)
    return action


@app.get("/health")
def health():
    return {"status": "ok"}
