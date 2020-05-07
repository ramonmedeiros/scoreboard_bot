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

    def get_userId_by_username(self, username, user_list=None):
        # not passed: get it
        if user_list is None:
            user_list = self.get_user_list()
            if user_list is False: return False

        for member in user_list["members"]:
            if len(member["profile"]["display_name"]) == 0:
                continue

            if member["profile"]["display_name"] in username:
                return member["id"]

    def get_name_by_id(self, userId, user_list=None):
        # not passed: get it
        if user_list is None:
            user_list = self.get_user_list()
            if user_list is False: return False

        for member in user_list["members"]:
            if member["id"] == userId:
                return member["real_name"]


    def get_user_list(self):
        try:
            return self.client.users_list()
        except Exception as e:
            logging.error(f"Error while retrieving users: {e}")
            return False


