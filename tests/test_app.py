import pytest
from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({'TESTING': True, 'DATABASE': str(tmp_path / 'test.sqlite3')})
    return app.test_client()


def test_ticket_lifecycle(client):
    response = client.post('/tickets/new', data={'title': 'Printer issue', 'description': 'The printer is not responding.', 'category': 'Hardware', 'priority': 'High'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Printer issue' in response.data
    assert b'Printer issue' in client.get('/').data
    response = client.post('/tickets/1', data={'status': 'Resolved'}, follow_redirects=True)
    assert b'selected>Resolved' in response.data


def test_validation_and_missing_ticket(client):
    response = client.post('/tickets/new', data={'title': 'x', 'description': 'short', 'category': 'Bad', 'priority': 'High'})
    assert response.status_code == 400
    assert b'Title must' in response.data
    assert b'No tickets yet' in client.get('/').data
    assert client.get('/tickets/999').status_code == 404
    assert client.post('/tickets/999', data={'status': 'Open'}).status_code == 404


def test_invalid_status_and_html_escaping(client):
    client.post('/tickets/new', data={'title': '<script>alert(1)</script>', 'description': 'A sufficiently long description', 'category': 'Other', 'priority': 'Low'})
    assert client.post('/tickets/1', data={'status': 'Invalid'}).status_code == 400
    page = client.get('/tickets/1').data
    assert b'&lt;script&gt;' in page and b'<script>' not in page
