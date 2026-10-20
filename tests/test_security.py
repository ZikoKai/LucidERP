def test_api_key(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret")
    assert client.get("/health").status_code == 200
    for path in (
        "/contacts",
        "/products",
        "/orders",
        "/invoices",
        "/agent-actions",
        "/docs",
        "/redoc",
        "/openapi.json",
    ):
        assert client.get(path).status_code == 401
        assert client.get(path, headers={"X-API-Key": "wrong"}).status_code == 401
        assert client.get(path, headers={"X-API-Key": "test-secret"}).status_code == 200
    for path in (
        "/agent/propose",
        "/agent-actions/1/approve",
        "/agent-actions/1/reject",
        "/orders/1/invoice",
    ):
        assert client.post(path, json={"text": "x", "decide_par": "Alice"}).status_code == 401


def test_cors(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret")
    response = client.options(
        "/orders",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-API-Key,Content-Type",
        },
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
