import pytest
from unittest.mock import patch, MagicMock

import scoreboard


@pytest.fixture
@patch('scoreboard.database.psycopg2')
@patch('scoreboard.slackApi.WebClient')
def client(webclient, db):
    app = scoreboard.startApp()
    app.config['TESTING'] = True

    return app.test_client()


def test_app(client):
    assert client.get("/").status_code == 404
