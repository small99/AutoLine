# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import requests


class GithubClient:

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = requests.session()

    def login(self):
        pass

    def logout(self):
        pass


if __name__ == "__main__":

    github = GithubClient("small99", "yangluoli0002")

