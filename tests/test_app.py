import pytest
from unittest.mock import patch, MagicMock

import scoreboard


@pytest.fixture
@patch('scoreboard.database.psycopg2')
@patch('scoreboard.slackApi.os.environ', {"SLACK_CLIENT_ID": "", "SLACK_CLIENT_SECRET": ""})
def client(db):
    app = scoreboard.startApp()
    app.config['TESTING'] = True
    app.config.dbMock = db

    return app.test_client()


def test_app(client):
    assert client.get("/").status_code == 302

def test_install(client):
    assert client.get("/install").status_code == 302




#@patch('scoreboard.slackApi.WebClient')
#def test_report_success(webclient, client):
#
#    # make sql works
#    client.application.config.db.get_token = MagicMock(return_value=[{"token": "token"}])
#    client.application.config.db.get_games_per_channel = MagicMock(return_value=[{"playerName1": "a",
#                                                                                  "playerName2": "b"}])
#
#    # post result
#    req = client.post("/result",
#                      data={"text": "1 1 @user",
#                            "user_name": "@bla",
#                            "channel_id": "AAA",
#                            "team_id": "aa"})
#
#    assert req.status_code == 200
#    assert req.json["message"] == "success"

@patch('scoreboard.slackApi.WebClient')
def test_report_text_wrong_format(webclient, client):

    # make sql works
    client.application.config.dbMock.connect().cursor().__enter__().rowcount = 1

    # post result
    req = client.post("/result",
                      data={"text": "1 1 ",
                            "user_name": "@bla",
                            "channel_id": "AAA",
                            "team_id": "aa"})

    assert req.status_code == 400

@patch('scoreboard.slackApi.WebClient')
def test_report_db_failed(webclient, client):

    # make sql works
    client.application.config.dbMock.connect().cursor().__enter__().execute.side_effect = Exception("BOOM")

    # post result
    req = client.post("/result",
                      data={"text": "1 1 @user",
                            "user_name": "@bla",
                            "channel_id": "AAA",
                            "team_id": "aa"})

    assert req.status_code == 400


