import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import hashlib
import hmac
import urllib
import scoreboard


@pytest.fixture
@patch('scoreboard.Database', MagicMock())
@patch('scoreboard.slackApi.os.environ', {"SLACK_CLIENT_ID": "", "SLACK_CLIENT_SECRET": "", "SLACK_SIGNING": "key"})
def client():
    app = scoreboard.startApp()
    app.config['TESTING'] = True
    return app.test_client()

def test_index(client):
    assert client.get("/").status_code == 302

def test_install(client):
    assert client.get("/install").status_code == 302


@patch('scoreboard.slackApi.Slack.add_to_workspace')
def test_oauth_token(res, client):
    # set workspace response
    res.return_value = {"team": {"id": ""},
                        "access_token": ""}

    # save token successful
    req = client.get("/redirect?code=")
    assert req.status_code == 200

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

@patch('scoreboard.generate_leaderboard')
@patch('scoreboard.slackApi.WebClient')
def test_validation(webclient, board, client):
    board.return_value = ""

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


@patch('scoreboard.Slack')
@patch('scoreboard.verify_request')
def test_report_result(verify, slackApi, client):

    # mock authentication and leaderboard return
    verify.return_value = True

    # request params
    req = client.post("/result",
                      data={"text": "1 1 @user",
                            "user_name": "@bla",
                            "channel_id": "AAA",
                            "team_id": "aa"})

    assert req.status_code == 204

@patch('scoreboard.Slack')
@patch('scoreboard.verify_request')
@patch('scoreboard.slackApi.WebClient')
def test_get_leaderboard(web, verify, slackApi, client):

    # mock authentication and leaderboard return
    verify.return_value = True
    client.application.config.db.get_token = MagicMock(return_value=[{"token": ""}])

    # mock information about games
    client.application.config.db.get_games_per_channel.return_value =[{"playerName1": "a",
                                                                       "playerName2": "b",
                                                                       "score1": 0,
                                                                       "score2": 0},
                                                                       {"playerName1": "a",
                                                                       "playerName2": "c",
                                                                       "score1": 1,
                                                                       "score2": 0},
                                                                       {"playerName1": "a",
                                                                        "playerName2": "b",
                                                                        "score1": 0,
                                                                        "score2": 1}]
    slackApi.get_name_by_id.return_value = "name"

    # request params
    req = client.post("/leaderboard",
                      data={"user_name": "@bla",
                            "channel_id": "AAA",
                            "team_id": "aa"})

    assert req.status_code == 204

@patch('scoreboard.slackApi.WebClient')
@patch('scoreboard.verify_request')
def test_report_text_wrong_format(verify, webclient, client):
    verify.return_value = True

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

    # post result
    req = client.post("/result",
                      data={"text": "1 1 @user",
                            "user_name": "@bla",
                            "channel_id": "AAA",
                            "team_id": "aa"})

    assert req.status_code == 400


