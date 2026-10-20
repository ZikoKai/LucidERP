import ast
from pathlib import Path


def test_propose_approve(client, catalog):
    action = client.post("/agent/propose", json={"text": "10 stylos pour Acme"})
    assert action.status_code == 201
    action = action.json()
    assert action["statut"] == "proposee"
    assert client.get("/orders").json() == []
    approved = client.post(f"/agent-actions/{action['id']}/approve", json={"decide_par": "Alice"})
    assert approved.status_code == 200
    assert approved.json()["decide_par"] == "Alice"
    assert approved.json()["decide_le"]
    assert approved.json()["order_id"]
    assert len(client.get("/orders").json()) == 1
    assert client.get("/orders").json()[0]["statut"] == "validee"
    assert (
        client.post(
            f"/agent-actions/{action['id']}/approve", json={"decide_par": "Bob"}
        ).status_code
        == 409
    )
    assert len(client.get("/orders").json()) == 1


def test_reject(client, catalog):
    action = client.post("/agent/propose", json={"text": "200 stylos pour Acme"}).json()
    assert action["risk_score"] == 50
    result = client.post(f"/agent-actions/{action['id']}/reject", json={"decide_par": "Alice"})
    assert result.json()["statut"] == "rejetee"
    assert client.get("/orders").json() == []
    assert len(client.get("/agent-actions?statut=rejetee").json()) == 1
    assert client.get("/agent-actions?statut=proposee").json() == []
    assert (
        client.post(
            f"/agent-actions/{action['id']}/approve", json={"decide_par": "Bob"}
        ).status_code
        == 409
    )


def test_parser_errors(client, catalog, monkeypatch):
    for text in ("do anything", "0 stylos pour Acme", "10 unknown pour Acme"):
        assert client.post("/agent/propose", json={"text": text}).status_code == 422
    monkeypatch.setenv("LLM_PROVIDER", "real")
    assert client.post("/agent/propose", json={"text": "10 stylos pour Acme"}).status_code == 501


def test_agent_cannot_write_orders():
    # Restrict every cross-module import, including the public sales interface.
    allowed = {
        "app.core": {"Base", "get_db"},
        "app.master_data": {"list_contacts", "list_products"},
        "app.sales": {"assess_order"},
    }
    forbidden = {"create_order", "SalesOrder", "SalesOrderLine", "exec", "eval", "__import__"}
    for path in Path("app/agent").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app."):
                assert node.module in allowed, path
                assert {alias.name for alias in node.names} <= allowed[node.module], path
            if isinstance(node, ast.Import):
                assert all(not alias.name.startswith("app") for alias in node.names), path
            if isinstance(node, ast.Name):
                assert node.id not in forbidden, path
            if isinstance(node, ast.Attribute):
                assert node.attr not in forbidden | {"execute", "exec_driver_sql"} or (
                    path.name == "service.py" and node.attr == "execute"
                ), path


def test_agent_proposal_cannot_call_creation(client, catalog, monkeypatch):
    import app.main
    import app.sales.service

    def forbidden(*args, **kwargs):
        raise AssertionError("Agent tried to create an order")

    monkeypatch.setattr(app.main, "create_order", forbidden)
    monkeypatch.setattr(app.sales.service, "create_order", forbidden)
    assert client.post("/agent/propose", json={"text": "10 stylos pour Acme"}).status_code == 201
    assert client.get("/orders").json() == []


def test_approval_rolls_back_on_failure(client, catalog, monkeypatch):
    from fastapi import HTTPException

    import app.main

    action = client.post("/agent/propose", json={"text": "10 stylos pour Acme"}).json()

    def fail(*args, **kwargs):
        raise HTTPException(422, "Simulated invalid order")

    monkeypatch.setattr(app.main, "create_order", fail)
    assert (
        client.post(
            f"/agent-actions/{action['id']}/approve", json={"decide_par": "Alice"}
        ).status_code
        == 422
    )
    pending = client.get("/agent-actions").json()[0]
    assert pending["statut"] == "proposee"
    assert pending["decide_par"] is None
    assert client.get("/orders").json() == []
