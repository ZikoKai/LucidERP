from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select, update

from app.master_data import list_contacts, list_products
from app.sales import assess_order

from .llm_client import get_llm_client
from .models import AgentAction
from .schemas import StructuredProposal


def propose(db, text):
    contacts = [{"id": c.id, "nom": c.nom, "type": c.type} for c in list_contacts(db)]
    products = [{"id": p.id, "nom": p.nom} for p in list_products(db)]
    try:
        proposal = StructuredProposal.model_validate(
            get_llm_client().parse_order_request(text, contacts, products)
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except NotImplementedError as exc:
        raise HTTPException(501, str(exc)) from exc
    lines, score, explanation = assess_order(db, proposal.contact_id, proposal.lines)
    action = AgentAction(
        raisonnement=proposal.reasoning,
        risk_score=score,
        risk_explanation=explanation,
        payload={"contact_id": proposal.contact_id, "lines": lines},
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def list_actions(db, statut=None):
    query = select(AgentAction).order_by(AgentAction.id.desc())
    if statut is not None:
        query = query.where(AgentAction.statut == statut)
    return db.scalars(query).all()


def claim_decision(db, action_id, decision, actor):
    """Atomically claim a pending decision. The caller commits the transaction."""
    action = db.get(AgentAction, action_id)
    if action is None:
        raise HTTPException(404, "Proposal not found")
    result = db.execute(
        update(AgentAction)
        .where(
            AgentAction.id == action_id,
            AgentAction.statut == "proposee",
        )
        .values(statut=decision, decide_par=actor, decide_le=datetime.now(UTC))
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Proposal has already been decided")
    db.refresh(action)
    return action


def attach_order(action, order_id):
    action.order_id = order_id
