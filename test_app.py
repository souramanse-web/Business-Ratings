import pytest
from app import app

@pytest.fixture

def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'<title>' in resp.data


def test_api_businesses(client):
    resp = client.get('/api/businesses')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_404_handler(client):
    resp = client.get('/route-that-does-not-exist')
    assert resp.status_code == 404
    assert resp.get_json().get('error') == 'Not found'
