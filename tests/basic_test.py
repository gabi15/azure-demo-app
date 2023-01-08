from app import app


def test_main_route():
    response = app.test_client().get('/')
    assert response.status_code == 200
