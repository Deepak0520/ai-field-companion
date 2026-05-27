from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_species_valid():
    response = client.get("/species/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Eucalyptus deglupta"

def test_get_species_invalid():
    response = client.get("/species/99")
    assert response.status_code == 200
    assert "error" in response.json()

def test_diagnose_leaf_blight():
    response = client.get("/diagnose/leaf_blight")
    assert response.status_code == 200
    assert response.json()["diagnosis"] == "Leaf Blight"

def test_diagnose_healthy():
    response = client.get("/diagnose/healthy")
    assert response.status_code == 200
    assert response.json()["severity"] == "none"
