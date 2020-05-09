import pytest
from unittest import patch, MagicMock

import scoreboard

@pytest.fixture

def client():
    app = scoreboard.startApp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_app(client):
    assert client.get("/").status_code == 404
