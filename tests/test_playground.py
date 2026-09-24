from fastapi.testclient import TestClient

from app.main import app


def test_playground_is_available():
    with TestClient(app) as client:
        response = client.get('/playground')
        assert response.status_code == 200
        assert 'Product Scraper API' in response.text
        assert 'Executar scrape' in response.text
        assert '/v1/scrape' in response.text


def test_root_redirects_to_playground():
    with TestClient(app) as client:
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 307
        assert response.headers['location'] == '/playground'
