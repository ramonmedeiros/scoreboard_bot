from slack import WebClient

import logging
import os


class Slack:
    def __init__(self, token):
        self.client_id = os.environ.get("SLACK_CLIENT_ID")
        self.client_secret = os.environ.get("SLACK_CLIENT_SECRET")
        self.client = self.connect(token)

    def connect(self, token):
        try:
            client = WebClient(token)
            logging.info(f"Connected with token {token[:6]}**{token[-6:]}")
        except Exception as e:
            logging.error(f"Cannot connect to Slack: {e}")
            return False

        return client

    def get_userId_by_username(self, username, user_list=None):
        # not passed: get it
        if user_list is None:
            user_list = self.get_user_list()
            if user_list is False: return False

        for member in user_list["members"]:
            if len(member["profile"]["display_name"]) == 0:
                continue

            if member["name"] in username:
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

    def add_to_workspace(self, code):
        try:
            response = self.client.oauth_v2_access(
               client_id=self.client_id,
               client_secret=self.client_secret,
               code=code
            )
        except Exception as e:
            logging.error(f"Cannot add workspace: {e}")
            return False
        return response
