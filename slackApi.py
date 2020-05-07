from slack import WebClient

import logging
import os

class Slack:
    def __init__(self):
        self.client = self.connect()

    def connect(self):
        token = os.environ.get("SLACK_BOT_TOKEN")
        if token is None:
            logging.error("Slack Token not found")

        return WebClient(token)


    def get_user_by_username(username):
        try:
            userlist = self.client.users_list()
        except Exception as e:
            logging.error(e)
            return

        for member in userlist["members"]:
            if len(member["profile"]["display_name"]) > 0 and member["profile"]["display_name"] in username:
                return member["id"]



