def order_payload(catalog, quantity=10, statut="brouillon"):
    contact, product = catalog
    return {
        "contact_id": contact["id"],
        "statut": statut,
        "lines": [{"product_id": product["id"], "quantite": quantity}],
    }


def test_orders(client, catalog):
    response = client.post("/orders", json=order_payload(catalog))
    assert response.status_code == 201
    order = response.json()
    assert order["risk_score"] == 0
    assert order["lines"][0]["prix_unitaire"] == "10.00"
    assert client.get(f"/orders/{order['id']}").json() == order
    risky = client.post("/orders", json=order_payload(catalog, 40)).json()
    assert risky["risk_score"] == 70
    assert len(client.get("/orders?min_risk=50").json()) == 1
    assert client.get("/orders?statut=validee").json() == []
    assert len(client.get(f"/orders?contact_id={catalog[0]['id']}").json()) == 2


def test_invalid_order(client, catalog):
    payload = order_payload(catalog)
    payload["lines"][0]["quantite"] = 0
    assert client.post("/orders", json=payload).status_code == 422
    payload = order_payload(catalog)
    payload["lines"] *= 2
    assert client.post("/orders", json=payload).status_code == 422
    payload = order_payload(catalog)
    payload["contact_id"] = 999
    assert client.post("/orders", json=payload).status_code == 404
