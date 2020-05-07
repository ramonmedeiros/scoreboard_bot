from flask import Flask, jsonify, request, make_response
from slack import WebClient

import os
import json
import logging
import requests

from database import Database

app = Flask(__name__)

# set up logging to file
logging.basicConfig(
     level=logging.INFO,
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
)
logging.getLogger(__name__)

def ack_response(url, text=""):
    try:
        a = requests.post(url, data={"text":text})
    except Exception as e:
        logging.error(e)
    logging.info(a.content)


def get_user_by_displayname(name):
    logging.info(f"Retriever user {name}")
    try:
        userlist = app.config.slack.users_list()
    except Exception as e:
        logging.error(e)
        return

    logging.info(userlist["members"])

    for member in userlist["members"]:
        if member["profile"]["display_name"] == name:
            logging.debug("User " + member["profile"]["real_name"])
            return member["profile"]["real_name"]

def get_user_by_username(username):
    try:
        userlist = app.config.slack.users_list()
    except Exception as e:
        logging.error(e)
        return

    logging.info(userlist["members"])
    for member in userlist["members"]:
        if member["name"] == username:
            return member["profile"]["real_name"]

def generate_leaderboard(channel):
    result = {}
    for game in GAME[channel]:
        if game["teamA"] not in result:
            result["teamA"] = {"win":0,
                               "loss": 0,
                               "draw": 0,
                               "scored": 0,
                               "defense": 0}
        if game["teamB"] not in result:
            result["teamB"] = {"win":0,
                               "loss": 0,
                               "draw": 0,
                               "scored": 0,
                               "defense": 0}
        result["teamA"]["scored"] += game["scoreA"]
        result["teamB"]["scored"] += game["scoreB"]
        result["teamA"]["defense"] += game["scoreB"]
        result["teamB"]["defense"] += game["scoreA"]

        # draw
        if game["scoreA"] == game["scoreB"]:
            result["teamA"]["draw"] += 1
            result["teamB"]["draw"] += 1

        elif game["scoreA"] > game["scoreB"]:
            result["teamA"]["win"] += 1
            result["teamB"]["loss"] += 1
        else:
            result["teamA"]["loss"] += 1
            result["teamB"]["win"] += 1

    return result

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
    int(myScore), int(otherScore), user = ret

    # get real names
    teamA = get_user_by_username(username)
    teamB = get_user_by_displayname(user)

    app.config.db.addGame(channel, teamA, myScore, teamB, otherScore)
    return jsonify(message="FOI")
#    return jsonify(generate_leaderboard(channel))

@app.route("/leaderboard", methods=['POST'])
def get_leaderboard():
    slack_response = request.form
    logging.info(slack_response)
    channel = slack_response["channel_id"]
    return jsonify(generate_leaderboard(channel))

def startApp():
    # Slack client for Web API requests
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    app.config.slack = WebClient(SLACK_BOT_TOKEN)

    app.config.db = Database()
    return app

