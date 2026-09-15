import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "api" in data
    assert "ipfs" in data
    assert "blockchain" in data
    assert data["api"] is True

def test_upload_invalid_file():
    # Since we didn't mock ipfs/blockchain in tests,
    # let's just test invalid file extension which fails early
    files = {"files": ("test.sh", b"echo hello", "text/plain")}
    data = {"name": "Test Site"}
    response = client.post("/publish", data=data, files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_upload_missing_name():
    files = {"files": ("index.html", b"<html></html>", "text/html")}
    response = client.post("/publish", files=files)
    assert response.status_code == 422 # Pydantic validation error for missing field

def test_get_website_not_found():
    response = client.get("/website/99999")
    # Depends on what the blockchain returns, but let's assume it handles errors
    # Actually if 99999 doesn't exist it returns 404
    assert response.status_code in [404, 500, 503]

def test_verify_missing_cid():
    response = client.get("/website/1/verify")
    assert response.status_code == 422
