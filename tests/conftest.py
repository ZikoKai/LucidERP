import os
import subprocess
import sys
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from app.core import get_db
from app.main import app


@pytest.fixture
def database_url(tmp_path):
    """Use SQLite by default, or isolate each PostgreSQL test in its own schema."""
    configured = os.getenv("TEST_DATABASE_URL")
    if not configured:
        yield f"sqlite:///{tmp_path / 'test.db'}"
        return
    url = make_url(configured)
    if url.get_backend_name() != "postgresql":
        raise ValueError("TEST_DATABASE_URL must point to a disposable PostgreSQL database")
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    schema = f"lucid_test_{uuid4().hex}"
    admin = create_engine(url)
    try:
        with admin.begin() as connection:
            connection.execute(CreateSchema(schema))
        isolated = url.update_query_dict({"options": f"-csearch_path={schema}"})
        yield isolated.render_as_string(hide_password=False)
    finally:
        with admin.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True, if_exists=True))
        admin.dispose()


@pytest.fixture
def client(database_url, monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    url = database_url
    # Migrate the test database using the same migration path as development.
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        env=dict(os.environ, DATABASE_URL=url),
        check=True,
    )
    engine = create_engine(
        url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {}
    )

    def override():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture
def catalog(client):
    contact = client.post("/contacts", json={"nom": "Acme"}).json()
    product = client.post(
        "/products",
        json={
            "nom": "stylos",
            "prix_unitaire": "10.00",
            "stock_declare": 20,
        },
    ).json()
    return contact, product
