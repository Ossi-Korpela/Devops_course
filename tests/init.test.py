import requests

def test_initial_state():
    resp = requests.put("http://localhost:8197/state", data="INIT")
    assert resp.status_code == 200

    resp = requests.get("http://localhost:8197/state")
    assert resp.json().text == 'INIT'



