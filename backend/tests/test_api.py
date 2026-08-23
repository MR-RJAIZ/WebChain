from fastapi.testclient import TestClient

from app.main import app


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