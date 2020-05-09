import pytest
from unittest.mock import patch, MagicMock

import scoreboard


@pytest.fixture
@patch('scoreboard.database.psycopg2')
@patch('scoreboard.slackApi.WebClient')
@patch('scoreboard.slackApi.os.environ', {"SLACK_BOT_TOKEN": ""})
def client(webclient, db):
    app = scoreboard.startApp()
    app.config['TESTING'] = True
    app.config.dbMock = db
    app.config.webclient = webclient

    return app.test_client()


def test_app(client):
    assert client.get("/").status_code == 404

def test_report_success(client):

    # make sql works
    client.application.config.dbMock.connect().cursor().__enter__().rowcount = 1

    # post result
    req = client.post("/result",
                      data={"text": "1 1 @user",
                            "user_name": "@bla",
                            "channel_id": "AAA",
                            "channel_name": "aa"})

    assert req.status_code == 204
    assert req.data == b""

def test_report_text_wrong_format(client):

    # make sql works
    client.application.config.dbMock.connect().cursor().__enter__().rowcount = 1

    # post result
    req = client.post("/result",
                      data={"text": "1 1 ",
                            "user_name": "@bla",
                            "channel_id": "AAA",
                            "channel_name": "aa"})

    assert req.status_code == 400

def test_report_db_failed(client):

    # make sql works
    client.application.config.dbMock.connect().cursor().__enter__().execute.side_effect = Exception("BOOM")

    # post result
    req = client.post("/result",
                      data={"text": "1 1 @user",
                            "user_name": "@bla",
                            "channel_id": "AAA",
                            "channel_name": "aa"})

    assert req.status_code == 500


