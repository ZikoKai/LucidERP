from test_orders import order_payload


def test_invoice_rules(client, catalog):
    draft = client.post("/orders", json=order_payload(catalog)).json()
    assert client.post(f"/orders/{draft['id']}/invoice").status_code == 409
    order = client.post("/orders", json=order_payload(catalog, statut="validee")).json()
    response = client.post(f"/orders/{order['id']}/invoice")
    assert response.status_code == 201
    assert response.json()["montant_total"] == "100.00"
    assert client.get(f"/orders/{order['id']}").json()["statut"] == "facturee"
    assert client.post(f"/orders/{order['id']}/invoice").status_code == 409
    assert len(client.get("/invoices").json()) == 1
    assert client.post("/orders/999/invoice").status_code == 404
