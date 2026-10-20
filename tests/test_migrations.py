import os
import subprocess
import sys

from sqlalchemy import create_engine, inspect


def test_migration(tmp_path):
    url = f"sqlite:///{tmp_path / 'migration.db'}"
    env = dict(os.environ, DATABASE_URL=url)
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], env=env, check=True)
    engine = create_engine(url)
    assert {"contacts", "products", "sales_orders", "invoices", "agent_actions"} <= set(
        inspect(engine).get_table_names()
    )
    engine.dispose()
    subprocess.run([sys.executable, "-m", "alembic", "downgrade", "base"], env=env, check=True)
