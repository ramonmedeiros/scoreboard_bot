import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import hashlib
import hmac
import urllib
import scoreboard


@pytest.fixture
@patch('scoreboard.database.psycopg2')
@patch('scoreboard.verify_request', True)
@patch('scoreboard.slackApi.os.environ', {"SLACK_CLIENT_ID": "", "SLACK_CLIENT_SECRET": "", "SLACK_SIGNING": "key"})
def client(db):
    app = scoreboard.startApp()
    app.config['TESTING'] = True
    app.config.dbMock = db

    return app.test_client()

def test_app(client):
    assert client.get("/").status_code == 302

def test_install(client):
    assert client.get("/install").status_code == 302

def test_old_timestamp(client):
    timestamp = datetime.now() - timedelta(minutes=6)
    ts = timestamp.timestamp()
    req = client.post("/leaderboard",
                      data={},
                      headers={'X-Slack-Request-Timestamp': ts})

    assert req.status_code == 401

def test_invalid_signature(client):
    # generate signature
    timestamp = datetime.now()
    ts = timestamp.timestamp()
    req = client.post("/leaderboard",
                      data={},
                      headers={'X-Slack-Request-Timestamp': ts})

    assert req.status_code == 401

@patch('scoreboard.slackApi.WebClient')
def test_validation(webclient, client):
    client.application.config.db.get_token = MagicMock(return_value=[{"token": ""}])
    scoreboard.generate_leaderboard = MagicMock(return_value="")

    # request params
    params={"text": "1 1 @user",
            "user_name": "@bla",
            "channel_id": "AAA",
            "team_id": "aa"}

    # generate signature
    timestamp = datetime.now()
    ts = timestamp.timestamp()
    request_body = urllib.parse.urlencode(params)
    sig_basestring = 'v0:' + str(ts) + ':' + request_body
    my_signature = 'v0=' + hmac.new("key".encode(),
                                    sig_basestring.encode(),
                                    hashlib.sha256).hexdigest()
    req = client.post("/leaderboard",
                      data=params,
                      headers={'X-Slack-Request-Timestamp': ts,
                               'X-Slack-Signature': my_signature})

    assert req.status_code == 204

@patch('scoreboard.slackApi.WebClient')
@patch('scoreboard.verify_request')
def test_report_text_wrong_format(verify, webclient, client):
    verify.return_value = True

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
@patch('scoreboard.verify_request')
def test_report_db_failed(verify, webclient, client):
    verify.return_value = True

    # make sql works
    client.application.config.dbMock.connect().cursor().__enter__().execute.side_effect = Exception("BOOM")

    # post result
    req = client.post("/result",
                      data={"text": "1 1 @user",
                            "user_name": "@bla",
                            "channel_id": "AAA",
                            "team_id": "aa"})

    assert req.status_code == 400


