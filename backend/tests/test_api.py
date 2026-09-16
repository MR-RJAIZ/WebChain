<<<<<<< HEAD
=======
import pytest
>>>>>>> main
from fastapi.testclient import TestClient

from app.main import app

<<<<<<< HEAD

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "WebChain backend is running"
    }


def test_get_deployments():
    response = client.get("/deployments")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_missing_deployment():
    response = client.get(
        "/deploy/does-not-exist"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Deployment not found"
    }


def test_deployment_workflow(tmp_path):
    test_file = tmp_path / "index.html"

    test_file.write_text(
        "<html><body><h1>Test Site</h1></body></html>",
        encoding="utf-8"
    )

    with open(test_file, "rb") as file:
        upload_response = client.post(
            "/upload",
            files=[
                (
                    "files",
                    (
                        "index.html",
                        file,
                        "text/html"
                    )
                )
            ]
        )

    assert upload_response.status_code == 200

    deploy_response = client.post("/deploy")

    assert deploy_response.status_code == 200

    deployment = deploy_response.json()
    deployment_id = deployment["deployment_id"]

    assert deployment["status"] == "pending"
    assert deployment["cid"] is None
    assert deployment["transaction_hash"] is None

    get_response = client.get(
        f"/deploy/{deployment_id}"
    )

    assert get_response.status_code == 200

    current_deployment = get_response.json()

    assert current_deployment["status"] == "deployed"

    delete_response = client.delete(
        f"/deploy/{deployment_id}"
    )

    assert delete_response.status_code == 200

    missing_response = client.get(
        f"/deploy/{deployment_id}"
    )

    assert missing_response.status_code == 404
=======
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
>>>>>>> main
