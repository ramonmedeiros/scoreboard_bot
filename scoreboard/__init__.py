import logging
import requests

from flask import Flask, current_app, jsonify, request, make_response, redirect

from .database import Database
from .slackApi import Slack


def oauth():
    auth_code = request.args['code']

    # An empty string is a valid token for this request
    slack = Slack(token='')

    # authenticate on slack: return error if present
    response = slack.add_to_workspace(auth_code)
    if response is False:
        return make_response(jsonify(message="Failed to authenticate"), 500)

    # save token
    teamId = response['team']['id']
    token = response["access_token"]
    logging.info(response)

    if current_app.config.db.save_token(teamId, token) is False:
        return make_response('', 500)

    # success
    return ('All set!', 200)

def post_result():
    slack_response = request.form
    logging.info(request.form)

    # get string sent by user
    teamId = slack_response['team_id']
    game_info = slack_response["text"]
    username = slack_response["user_name"]
    channel = slack_response["channel_id"]

    ret = game_info.split()
    if len(ret) != 3:
        return make_response(jsonify(message="You need to send in the format"), 400)

    # parse data and add to games
    myScore, otherScore, user = ret

    # set up slack
    token = current_app.config.db.get_token(teamId)
    if token is False:
        return make_response(jsonify(message="Not authenticated on Slack"), 400)
    slack = Slack(token=token[0]["token"])

    # get real names
    teamA = slack.get_userId_by_username(username)
    teamB = slack.get_userId_by_username(user)

    # error while saving: report
    if current_app.config.db.addGame(channel, teamA, int(myScore), teamB, int(otherScore)) is False:
        return make_response(jsonify(message="Cannot register game"), 500)

    msg = generate_leaderboard(channel, token[0]["token"])
    logging.info(f"Sending message on channel {channel}: {msg}")
    slack.client.chat_postMessage(channel=channel, text=msg)
    return jsonify(message="success")


def get_leaderboard():
    logging.info(request.form)
    slack_response = request.form
    channel = slack_response["channel_id"]
    teamId = slack_response['team_id']

    # set up slack
    token = current_app.config.db.get_token(teamId)
    if token is False:
        return make_response(jsonify(message="Not authenticated on Slack"), 400)
    slack = Slack(token=token[0]["token"])

    msg = generate_leaderboard(channel, token[0]["token"])
    logging.info(f"Sending message on channel {channel}: {msg}")
    slack.client.chat_postMessage(channel=channel, text=msg)

    return jsonify(message="success")


def generate_leaderboard(channel, token):
    result = current_app.config.db.get_games_per_channel(channel)

    # no result: return empty
    if result is False:
        return jsonify(message="No game")

    # cache user list
    slack = Slack(token=token)
    userList = slack.get_user_list()

    # generate table
    board = {}
    for game in result:
        player1 = slack.get_name_by_id(game['playerName1'], userList)
        player2 = slack.get_name_by_id(game['playerName2'], userList)

        # not present: add
        if player1 not in board:
            board[player1] = {"win": 0, "lost": 0, "draw": 0, "goals": 0}
        if player2 not in board:
            board[player2] = {"win": 0, "lost": 0, "draw": 0, "goals": 0}

        # check result
        if game['score1'] > game['score2']:
            board[player1]["win"] += 1
            board[player2]["lost"] += 1
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

    # order by wins and return
    final = []
    for player in board:
        p = board[player]
        l = [p["win"], p["draw"], p["lost"], p["goals"]]
        l.insert(0, player)
        final.append(l)

    # sort by win DESC
    final.sort(key=lambda x: x[1], reverse=True)

    # add header
    st = "```\n"
    spaceName = 30
    st += "Name" + (spaceName - 4) * " " + "Wins Draws Lost Goals\n"

    for player in final:
        space = spaceName - len(player[0])
        st += player[0] + space * " " + "  " + "    ".join(map(
            str, player[1:])) + "\n"
    st += "```\n"
    return st



def index():
    return redirect("https://github.com/ramonmedeiros/scoreboard_bot/", code=302)

def install():
    return redirect("https://slack.com/oauth/v2/authorize?client_id=4022839166.989674812551&scope=commands,users:read,chat:write", code=302)

def startApp():
    # start app and set logging
    app = Flask(__name__)
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(__name__)

    # add endpoints
    app.add_url_rule('/', 'index', index, methods=['GET'])
    app.add_url_rule('/install', 'install', install, methods=['GET'])
    app.add_url_rule('/redirect', 'oauth', oauth, methods=['POST', 'GET'])
    app.add_url_rule('/result', 'post_result', post_result, methods=['POST'])
    app.add_url_rule('/leaderboard',
                     'get_leaderboard',
                     get_leaderboard,
                     methods=['POST'])

    # add db and slack client
    app.config.db = Database()
    return app
