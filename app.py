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
    teamA = app.config.slack.get_userId_by_username(username)
    teamB = app.config.slack.get_userId_by_username(user)

    app.config.db.addGame(channel, teamA, int(myScore), teamB, int(otherScore))
    return jsonify(generate_leaderboard(channel))

@app.route("/leaderboard", methods=['POST'])
def get_leaderboard():
    slack_response = request.form
    logging.info(slack_response)
    channel = slack_response["channel_id"]
    return jsonify(board=generate_leaderboard(channel))

def generate_leaderboard(channel):
    result = app.config.db.get_games_per_channel(channel)

    # no result: return empty
    if result is False:
        return jsonify(message="No game")

    # cache user list
    userList = app.config.slack.get_user_list()

    # generate table
    board = {}
    for game in result:
        player1 = app.config.slack.get_name_by_username(game['playerName1'], userList)
        player2 = app.config.slack.get_name_by_username(game['playerName2'], userList)

        # not present: add
        if player1 not in board: board[player1] = {"win": 0, "lost": 0, "draw": 0, "goals": 0}
        if player2 not in board: board[player2] = {"win": 0, "lost": 0, "draw": 0, "goals": 0}

        # check result
        if game['score1'] > game['score2']:
            board[player1]["win"] += 1
            board[player1]["lost"] += 1
        elif game['score1'] == game['score2']:
            board[player1]["draw"] += 1
            board[player2]["draw"] += 1
        else:
            board[player2]["win"] += 1
            board[player1]["lost"] += 1

        # sum goals
        diff = game['score1'] - game['score2']
        board[player1]["goals"] += diff
        board[player2]["goals"] += (diff * -1)

    return board

def startApp():
    # set logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__)

    # Slack client for Web API requests
    app.config.db = Database()
    app.config.slack = Slack()
    return app

