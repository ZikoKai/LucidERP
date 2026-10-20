from alembic import context

from app.agent.models import AgentAction  # noqa: F401
from app.core.db import Base, engine
from app.master_data.models import Contact, Product  # noqa: F401
from app.sales.models import Invoice, SalesOrder, SalesOrderLine  # noqa: F401

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
