from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_guest_link():
    # Simulate a POST request from a guest client
    response = client.post("/links", json={"url": "https://www.google.com"})

    # Verify the server returns 201 Created
    assert response.status_code == 201

    # Verify the response contains the short_code
    data = response.json()
    assert "short_code" in data


def test_redirect_not_found():
    # Attempt to access a non-existent link
    response = client.get("/this-code-does-not-exist")

    # Must return 404 Not Found
    assert response.status_code == 404


def test_custom_alias_conflict():
    # Create a link with a custom alias
    response1 = client.post(
        "/links",
        json={"url": "https://www.github.com", "custom_alias": "my-unique-alias"},
    )
    assert response1.status_code == 201

    # Attempt to create another link with the exact same alias
    response2 = client.post(
        "/links",
        json={"url": "https://www.linkedin.com", "custom_alias": "my-unique-alias"},
    )

    # Server must recognize the conflict and return 409
    assert response2.status_code == 409
