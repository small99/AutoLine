# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

from datetime import datetime
from flask import url_for
from flask_restful import Resource, reqparse
from flask_login import current_user

from ..models import User, Role
from .. import db


class Users(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=str)
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('email', type=str)
        self.parser.add_argument('username', type=str)
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('password', type=str)
        self.parser.add_argument('role_id', type=int)

        self.parser.add_argument('page', type=int, default=1)
        self.parser.add_argument('rows', type=int, default=15)

    def get(self):
        args = self.parser.parse_args()
        pagination = User.query.order_by(User.id.desc()).paginate(
            args["page"], per_page=args["rows"],
            error_out=False
        )
        users = pagination.items
        data = {"total": pagination.total, "rows": []}
        for u in users:
            data["rows"].append({
                "id": u.id,
                "role_id": u.role_id,
                "email": u.email,
                "用户名": u.username,
                "昵称": u.name,
                "角色": Role.query.filter_by(id=u.role_id).first().name,
                "最后在线时间": u.last_seen.strftime("%Y-%m-%d %H:%M:%S")
            })

        return data

    def post(self):
        args = self.parser.parse_args()

        method = args["method"].lower()
        if method == "create":
            return self.__create(args)
        elif method == "edit":
            return self.__edit(args)
        elif method == "delete":
            return self.__delete(args)

    def __create(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        user = User.query.filter_by(email=args["email"]).first()
        if user is None:
            try:
                u = User(username=args["username"],
                         email=args["email"],
                         role_id=args["role_id"],
                         password=args["password"],
                         name=args["username"])

                db.session.add(u)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "异常: %s" % str(e)
        else:
            result["status"] = "fail"
            result["msg"] = "email[%s]重复" % args["email"]

        return result

    def __edit(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}
        user = User.query.filter_by(id=args["id"]).first()
        if user is None:
            result["status"] = "fail"
            result["msg"] = "未找到要修改的用户"
        else:
            try:
                user.role_id = args["role_id"]
                user.username = args["username"]
                user.name = args["name"]
                user.password = args["password"]
                user.email = args["email"]

                db.session.merge(user)
                db.session.commit()

            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "编辑用户[id-%s]失败：%s" % (args["id"], str(e))

        return result

    def __delete(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        user = User.query.filter_by(id=args["id"]).first()
        if user is None:
            result["status"] = "fail"
            result["msg"] = "未找到要删除的用户"
        else:
            try:
                if user.verify_password(args["password"]):
                    db.session.delete(user)
                    db.session.commit()
                else:
                    result["status"] = "fail"
                    result["msg"] = "删除用户[email-%s]失败：密码错误" % user.email
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "删除用户[id-%s]失败：%s" % (args["id"], str(e))

        return result
