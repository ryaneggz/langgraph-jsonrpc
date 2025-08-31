"""Basic JSON-RPC functionality tests.

Tests core JSON-RPC 2.0 functionality including method calls,
error handling, and batch requests.
"""



def test_ping(client):
    """Test basic ping method."""
    response = client.post(
        "/rpc", 
        json={"jsonrpc": "2.0", "method": "ping", "id": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["result"] == "pong"
    assert data["id"] == 1
    assert data.get("error") is None


def test_math_add(client):
    """Test math.add method with valid parameters."""
    response = client.post(
        "/rpc", 
        json={
            "jsonrpc": "2.0",
            "method": "math.add",
            "params": {"a": 2.5, "b": 3.7},
            "id": "test-add"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["result"] == 6.2
    assert data["id"] == "test-add"


def test_math_subtract(client):
    """Test math.subtract method."""
    response = client.post(
        "/rpc", 
        json={
            "jsonrpc": "2.0",
            "method": "math.subtract",
            "params": {"a": 10.0, "b": 3.0},
            "id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 7.0


def test_math_multiply(client):
    """Test math.multiply method."""
    response = client.post(
        "/rpc", 
        json={
            "jsonrpc": "2.0",
            "method": "math.multiply",
            "params": {"a": 4.0, "b": 2.5},
            "id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 10.0


def test_method_not_found(client):
    """Test error response for non-existent method."""
    response = client.post(
        "/rpc", 
        json={"jsonrpc": "2.0", "method": "nonexistent", "id": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32601
    assert "not found" in data["error"]["message"].lower()
    assert data["id"] == 1


def test_invalid_params(client):
    """Test error response for invalid parameters."""
    response = client.post(
        "/rpc", 
        json={
            "jsonrpc": "2.0",
            "method": "math.add",
            "params": {"a": "not_a_number", "b": 3},
            "id": 1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32602


def test_notification(client):
    """Test notification (request without id)."""
    response = client.post(
        "/rpc", 
        json={"jsonrpc": "2.0", "method": "ping"}
    )
    assert response.status_code == 200
    # Notifications should return empty string
    assert response.text == '""'


def test_batch_requests(client):
    """Test batch request processing."""
    batch = [
        {"jsonrpc": "2.0", "method": "ping", "id": 1},
        {"jsonrpc": "2.0", "method": "nonexistent", "id": 2},
        {"jsonrpc": "2.0", "method": "math.add", "params": {"a": 1, "b": 1}, "id": 3},
        {"jsonrpc": "2.0", "method": "ping"},  # notification
    ]
    response = client.post("/rpc", json=batch)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 3  # notification doesn't return response
    
    # Check response IDs
    response_ids = {item["id"] for item in data}
    assert response_ids == {1, 2, 3}
    
    # Find specific responses
    ping_response = next(item for item in data if item["id"] == 1)
    error_response = next(item for item in data if item["id"] == 2)
    add_response = next(item for item in data if item["id"] == 3)
    
    assert ping_response["result"] == "pong"
    assert "error" in error_response
    assert add_response["result"] == 2


def test_batch_all_notifications(client):
    """Test batch request with all notifications."""
    batch = [
        {"jsonrpc": "2.0", "method": "ping"},
        {"jsonrpc": "2.0", "method": "ping"},
    ]
    response = client.post("/rpc", json=batch)
    assert response.status_code == 200
    # All notifications should return empty string
    assert response.text == '""'


def test_invalid_json(client):
    """Test error response for invalid JSON."""
    response = client.post(
        "/rpc", 
        data="{invalid json}",
        headers={"content-type": "application/json"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32700  # Parse error
    assert data.get("id") is None


def test_invalid_request_structure(client):
    """Test error response for invalid request structure."""
    response = client.post(
        "/rpc", 
        json={"jsonrpc": "1.0", "method": "ping", "id": 1}  # wrong jsonrpc version
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32600  # Invalid Request


def test_missing_method_in_request(client):
    """Test error response for request without method."""
    response = client.post(
        "/rpc", 
        json={"jsonrpc": "2.0", "id": 1}  # missing method
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32600  # Invalid Request
