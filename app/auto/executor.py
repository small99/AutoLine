# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

import requests


def run_job(id):
    s = requests.Session()

    r = s.post("http://127.0.0.1:5000/api/v1/auth/",
               data={"email": "AutoExecutor@126.com", "password": "123456", "method": "login"})

    s.get("http://127.0.0.1:5000/test_run/auto/%s" % id)

