import pytest
from app import app

@pytest.fixture

def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_chat(client):
    resp = client.post('/chat', json={'message': 'hi'})
    assert resp.status_code == 200
    assert 'response' in resp.get_json()


def test_alert_missing(client):
    resp = client.post('/alert', json={})
    assert resp.status_code == 400

# predictions and alerts require network and yfinance; skip in CI
def test_predict_no_symbol(client):
    resp = client.post('/predict', json={})
    assert resp.status_code == 400


def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'<title>' in resp.data
