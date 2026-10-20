"""Initial ERP schema."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nom", sa.String, nullable=False),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("ville", sa.String, nullable=False),
        sa.CheckConstraint("type IN ('client', 'fournisseur')"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nom", sa.String, nullable=False),
        sa.Column("prix_unitaire", sa.Numeric(14, 2), nullable=False),
        sa.Column("stock_declare", sa.Integer, nullable=False),
        sa.CheckConstraint("prix_unitaire >= 0 AND stock_declare >= 0"),
    )
    op.create_table(
        "sales_orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("contact_id", sa.Integer, sa.ForeignKey("contacts.id"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("statut", sa.String, nullable=False),
        sa.Column("risk_score", sa.Integer, nullable=False),
        sa.Column("risk_explanation", sa.String, nullable=False),
        sa.CheckConstraint("statut IN ('brouillon', 'validee', 'facturee')"),
    )
    op.create_table(
        "sales_order_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("sales_orders.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantite", sa.Integer, nullable=False),
        sa.Column("prix_unitaire", sa.Numeric(14, 2), nullable=False),
        sa.CheckConstraint("quantite > 0 AND prix_unitaire >= 0"),
    )
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "order_id", sa.Integer, sa.ForeignKey("sales_orders.id"), nullable=False, unique=True
        ),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("montant_total", sa.Numeric(14, 2), nullable=False),
        sa.Column("statut", sa.String, nullable=False),
    )
    op.create_table(
        "agent_actions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("sales_orders.id")),
        sa.Column("acteur", sa.String, nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("raisonnement", sa.String, nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("statut", sa.String, nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("risk_score", sa.Integer, nullable=False),
        sa.Column("risk_explanation", sa.String, nullable=False),
        sa.Column("decide_par", sa.String),
        sa.Column("decide_le", sa.DateTime(timezone=True)),
        sa.CheckConstraint("acteur IN ('human', 'agent')"),
        sa.CheckConstraint("statut IN ('proposee', 'approuvee', 'rejetee')"),
    )


def downgrade():
    for table in (
        "agent_actions",
        "invoices",
        "sales_order_lines",
        "sales_orders",
        "products",
        "contacts",
    ):
        op.drop_table(table)
