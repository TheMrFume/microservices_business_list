from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_valid_token():
    # Prepare valid token and headers
    valid_token = '{"user_token":"sample_token","user_id":"1234"}'
    headers = {
        "X-Token": valid_token,
        "X-Correlation-ID": "test-correlation-id"
    }

    # Send request
    response = client.get("/composite/view_full_list?list_id=1", headers=headers)

    # Check response
    assert response.status_code == 200
    print(response.json())  # Optional: Print the response for debugging


def test_invalid_token_format():
    # Prepare invalid token
    invalid_token = 'invalid_token_format'
    headers = {
        "X-Token": invalid_token,
        "X-Correlation-ID": "test-correlation-id"
    }

    # Send request
    response = client.get("/composite/view_full_list?list_id=1", headers=headers)

    # Check response
    assert response.status_code == 400
    assert response.json()["detail"] == "Access denied: Invalid token format."


def test_missing_token():
    headers = {
        "X-Correlation-ID": "test-correlation-id"
    }

    response = client.get("/composite/view_full_list?list_id=1", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Access denied: Missing token."
