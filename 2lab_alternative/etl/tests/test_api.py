from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)



def test_create_item():

    # сначала создаём source (если нужно)
    source_response = client.post("/sources", json={
        "name": "Test Source",
        "base_url": "https://test.com"
    })

    source_id = source_response.json()["id"]

    response = client.post("/items", json={
        "title": "iPhone 15",
        "description": "Smartphone",
        "price": 1200,
        "source_id": source_id
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "iPhone 15"
    assert "id" in data



def test_put_item():

    source = client.post("/sources", json={
        "name": "S1",
        "base_url": "https://s1.com"
    }).json()

    item = client.post("/items", json={
        "title": "Old",
        "description": "Old",
        "price": 100,
        "source_id": source["id"]
    }).json()

    response = client.put(f"/items/{item['id']}", json={
        "title": "New",
        "description": "New",
        "price": 200,
        "source_id": source["id"]
    })

    assert response.status_code == 200
    assert response.json()["title"] == "New"



def test_patch_item():

    source = client.post("/sources", json={
        "name": "S2",
        "base_url": "https://s2.com"
    }).json()

    item = client.post("/items", json={
        "title": "PatchTest",
        "description": "desc",
        "price": 100,
        "source_id": source["id"]
    }).json()

    response = client.patch(f"/items/{item['id']}", json={
        "price": 999
    })

    assert response.status_code == 200
    assert response.json()["price"] == 999



def test_delete_item():

    source = client.post("/sources", json={
        "name": "S3",
        "base_url": "https://s3.com"
    }).json()

    item = client.post("/items", json={
        "title": "ToDelete",
        "description": "desc",
        "price": 100,
        "source_id": source["id"]
    }).json()

    response = client.delete(f"/items/{item['id']}")

    assert response.status_code == 200



def test_get_not_found():

    response = client.get("/items/999999")

    assert response.status_code == 404