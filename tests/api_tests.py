import pytest
import requests
from requests.auth import HTTPBasicAuth
import time

BASE_URL = "http://host.docker.internal:8197"
AUTH = HTTPBasicAuth("admin", "secret")
TIMEOUT = 5

def put_to(state):
    return requests.put(
            f"{BASE_URL}/state",
            params={"state": state},
            auth=AUTH,
            timeout=TIMEOUT
        )

@pytest.mark.order(1)
def test_initial_state():

    resp = requests.get(f"{BASE_URL}/state")
    valid_states = ["INIT", "PAUSED", "RUNNING", "SHUTDOWN"]
    assert resp.text in valid_states
    time.sleep(0.1)

@pytest.mark.order(2)
def test_state_change_no_auth():
    """
      Shouldn't allow state change without login (401)
    """
    states_to_test = ["PAUSED", "RUNNING"]
    for state in states_to_test:
        # try changing state without auth
        response = requests.put(
            f"{BASE_URL}/state",
            params={"state": state},
            timeout=TIMEOUT
        )
        assert response.status_code == 401, (
            f"Expected 401 for unauthenticated state change to {state}, "
            f"got {response.status_code}"
        )
        assert "401" in response.text or "Unauthorized" in response.text, (
            "Expected error page to contain '401' or 'Unauthorized'"
        )
    time.sleep(0.1)

@pytest.mark.order(3)
def test_state_change_admin():
    """
      Should allow state change after login as admin
    """
    states_to_test = ["PAUSED", "RUNNING"]
    for state in states_to_test:
        response = put_to(state)
        assert response.status_code == 200, (
            f"Expected 200 when changing state to {state} as admin, "
            f"got {response.status_code}"
        )
        
        assert response.text.strip() == state, (
            f"Expected response body to be '{state}', got '{response.text}'"
        )
    time.sleep(2)

@pytest.mark.order(4)
def test_ex4_functionality():
    response = put_to("RUNNING")
    assert response.status_code == 200, "state changes should work as before"

    
    response = requests.get(f"{BASE_URL}/api", timeout=TIMEOUT)
    assert response.status_code == 200, "Expected 200 from /api endpoint"
    data = response.json()
    assert "Service1" in data, "Expected 'Service1' in the response JSON"
    assert "Service2" in data, "Expected 'Service2' in the response JSON"
    time.sleep(2)

@pytest.mark.order(5)
def test_run_log():
    """
      Should return the run log
    """
    response = requests.get(f"{BASE_URL}/run-log", timeout=TIMEOUT)
    assert response.status_code == 200, "Expected 200 from /run-log endpoint"
    assert isinstance(response.text, str), "Expected run log response to be a string"

@pytest.mark.order(6)
def test_run_log_changes():
    """
      Should return the run log containing correct state changes
    """
    response = put_to("INIT")
    assert response.status_code == 200, "state changes should work as before"
    response = put_to("RUNNING")
    assert response.status_code == 200, "state changes should work as before"
    
    response = requests.get(f"{BASE_URL}/run-log", timeout=TIMEOUT)
    assert response.status_code == 200, "Expected 200 from /run-log endpoint after changes to state"
    assert isinstance(response.text, str)
    assert response.text.find("INIT->RUNNING") != -1, f"Expected response to contain 'INIT->RUNNING', was {response.text}"
    time.sleep(2)

@pytest.mark.order(7)
def test_paused_state_changes():
    response = put_to("INIT")
    assert response.status_code == 200, "state changes should work as before"
    response = put_to("PAUSED")
    assert response.status_code == 200, "state changes should work as before"

    response = requests.get(f"{BASE_URL}/api", timeout=TIMEOUT)
    assert response.status_code == 503, "Should be paused"


    response = put_to("RUNNING")
    assert response.status_code == 200, "state changes should work as before"
    time.sleep(2)

    response = requests.get(f"{BASE_URL}/api", timeout=TIMEOUT)
    assert response.status_code == 200, "Expected 200 from /api endpoint"
