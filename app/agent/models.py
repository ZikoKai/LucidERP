from datetime import UTC, datetime

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class AgentAction(Base):
    __tablename__ = "agent_actions"
    __table_args__ = (
        CheckConstraint("acteur IN ('human', 'agent')"),
        CheckConstraint("statut IN ('proposee', 'approuvee', 'rejetee')"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("sales_orders.id"))
    acteur: Mapped[str] = mapped_column(default="agent")
    action: Mapped[str] = mapped_column(default="create_order")
    raisonnement: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    statut: Mapped[str] = mapped_column(default="proposee")
    payload: Mapped[dict] = mapped_column(JSON)
    risk_score: Mapped[int]
    risk_explanation: Mapped[str]
    decide_par: Mapped[str | None]
    decide_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
