# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

from datetime import datetime

from flask import url_for
from flask_restful import Resource, reqparse
from flask_login import login_user, logout_user
from ..models import User


class Auth(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str)
        self.parser.add_argument('password', type=str)
        self.parser.add_argument('method', type=str)

    def post(self):
        args = self.parser.parse_args()
        email = args["email"]
        password = args["password"]
        method = args["method"]
        if method == "login":
            user = User.query.filter_by(email=email).first()

            if user is not None and user.verify_password(password):
                login_user(user, True)

                return {"status": "success",
                        "msg": "登录成功",
                        "url": url_for("main.dashboard")}, 201

            return {"status": "fail",
                    "msg": "email或密码错误",
                    "url": url_for("main.index")}, 201
        elif method == "logout":

            logout_user()

            return {"status": "success",
                    "msg": "注销成功",
                    "url": url_for("main.index")}, 201

        return {"status": "success",
                "msg": "返回首页",
                "url": url_for("main.index")}, 201
