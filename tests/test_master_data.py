def test_master_data(client, catalog):
    contact, product = catalog
    assert client.get(f"/contacts/{contact['id']}").json()["type"] == "client"
    assert len(client.get("/contacts").json()) == 1
    assert client.get(f"/products/{product['id']}").json()["stock_declare"] == 20
    assert len(client.get("/products").json()) == 1
    assert client.get("/contacts/999").status_code == 404
    assert client.post("/products", json={"nom": "bad", "prix_unitaire": -1}).status_code == 422
