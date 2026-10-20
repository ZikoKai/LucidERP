import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core import get_db
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    url = f"sqlite:///{tmp_path / 'test.db'}"
    # Migrate the test database using the same migration path as development.
    import subprocess
    import sys

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        env=dict(os.environ, DATABASE_URL=url),
        check=True,
    )
    engine = create_engine(url, connect_args={"check_same_thread": False})

    def override():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
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
