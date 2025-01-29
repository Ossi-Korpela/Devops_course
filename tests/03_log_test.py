import pytest
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://host.docker.internal:8197"
AUTH = HTTPBasicAuth("admin", "secret")
TIMEOUT = 5


def test_run_log():
    """
      Should return the run log
    """
    response = requests.get(f"{BASE_URL}/run-log", timeout=TIMEOUT)
    assert response.status_code == 200, "Expected 200 from /run-log endpoint"
    assert isinstance(response.text, str), "Expected run log response to be a string"

def test_run_log_changes():
    """
      Should return the run log containing correct state changes
    """
    response = requests.put(
            f"{BASE_URL}/state",
            params={"state": "INIT"},
            auth=AUTH,
            timeout=TIMEOUT
        )
    response = requests.put(
            f"{BASE_URL}/state",
            params={"state": "RUNNING"},
            auth=AUTH,
            timeout=TIMEOUT
        )
    
    response = requests.get(f"{BASE_URL}/run-log", timeout=TIMEOUT)
    assert response.status_code == 200, "Expected 200 from /run-log endpoint after changes to state"
    assert isinstance(response.text, str)
    assert response.text.find("INIT->RUNNING") != -1, "Expected response to contain 'INIT->RUNNING'"