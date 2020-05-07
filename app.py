from flask import Flask, jsonify, request
from slack import WebClient
import os
import json
import logging
import requests
app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

# Slack client for Web API requests

# save game history
GAME_PATH = "/home/ramonmedeiros/mysite/game.json"

client = WebClient(SLACK_BOT_TOKEN)

def save_game():
    global GAME
    global GAME_PATH

    # delete if exists
    if os.path.exists(GAME_PATH):
        os.remove(GAME_PATH)

    # save
    with open(GAME_PATH, "w") as fd:
        fd.write(json.dumps(GAME))

def load_game():
    global GAME
    global GAME_PATH

    with open(GAME_PATH) as fd:
        return json.loads(fd.read())

def ack_response(url, text=""):
    try:
        a = requests.post(url, data={"text":text})
    except Exception as e:
        logging.error(e)
    logging.info(a.content)


def get_user_by_displayname(name):
    global client
    try:
        userlist = client.users_list()
    except Exception as e:
        logging.error(e)
        return

    for member in userlist["members"]:
        if member["profile"]["display_name"] == name:
            return member["profile"]["real_name"]

def get_user_by_username(username):
    try:
        userlist = client.users_list()
    except Exception as e:
        logging.error(e)
        return

    for member in userlist["members"]:
        if member["name"] == username:
            return member["profile"]["real_name"]

def newGame(channel, teamA, teamB, scoreA, scoreB):
    # add game results
    global GAME
    if channel not in GAME:
        GAME[channel] = []

    GAME[channel].append({"teamA": teamA,
                          "teamB": teamB,
                          "scoreA": scoreA,
                          "scoreB": scoreB})
    save_game()

def generate_leaderboard(channel):
    global GAME
    if channel not in GAME:
        return ""

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
    myScore, otherScore, user = ret

    # get real names
    teamA = get_user_by_username(username)
    teamB = get_user_by_displayname(user)

    newGame(channel, teamA, teamB, myScore, otherScore)
    return jsonify(generate_leaderboard(channel))

@app.route("/leaderboard", methods=['POST'])
def get_leaderboard():
    slack_response = request.form
    logging.info(slack_response)
    channel = slack_response["channel_id"]
    return jsonify(generate_leaderboard(channel))

def startApp():
    # load game if exists
    logging.info(f"Os environ: {os.environ}")
    GAME = {}
    if os.path.exists(GAME_PATH):
        load_game()
    return app

