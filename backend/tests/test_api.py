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