import logging
import requests

from flask import Flask, current_app, jsonify, request, make_response

from database import Database
from slackApi import Slack

app = Flask(__name__)


@app.route("/result", methods=['POST'])
def post_result():
    slack_response = request.form
    logging.info(slack_response)

    # get string sent by user
    game_info = slack_response["text"]
    username = slack_response["user_name"]
    channel = slack_response["channel_id"]

    ret = game_info.split()
    if len(ret) != 3:
        return jsonify({"text": "You need to send in the format"})

    # parse data and add to games
    myScore, otherScore, user = ret

    # get real names
    teamA = app.config.slack.get_user_by_username(username)
    teamB = app.config.slack.get_user_by_username(user)

    app.config.db.addGame(channel, teamA, int(myScore), teamB, int(otherScore))
    return jsonify(message="FOI")
#    return jsonify(app.config.db.get_leaderboard(channel))

@app.route("/leaderboard", methods=['POST'])
def get_leaderboard():
    slack_response = request.form
    logging.info(slack_response)
    channel = slack_response["channel_id"]
    return jsonify(app.config.db.get_leaderboard(channel))

def startApp():
    # set logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__)

    # Slack client for Web API requests
    app.config.db = Database()
    app.config.slack = Slack()
    return app

