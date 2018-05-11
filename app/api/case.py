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
from sqlalchemy import and_

from ..models import AutoSuite, AutoCase, User
from .. import db


class Case(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int)
        self.parser.add_argument('suite_id', type=int)
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('desc', type=str)
        self.parser.add_argument('tags', type=str)
        self.parser.add_argument('prev', type=int)
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('enable', type=bool, default=True)
        self.parser.add_argument('setup', type=str)
        self.parser.add_argument('teardown', type=str)
        self.parser.add_argument('page', type=int, default=1)
        self.parser.add_argument('rows', type=int, default=15)

    def get(self):
        args = self.parser.parse_args()

        pagination = AutoCase.query.filter_by(suite_id=args["suite_id"]).order_by(AutoCase.id.asc()).paginate(
            args["page"], per_page=args["rows"],
            error_out=False
        )

        cases = pagination.items
        data = {"total": pagination.total, "rows": []}
        for v in cases:
            data["rows"].append({
                "id": v.id,
                "suite_id": v.suite_id,
                "名称": v.name,
                "描述": v.desc,
                "创建人": User.query.filter_by(id=v.create_author_id).first().username,
                "创建日期": v.create_timestamp.strftime("%Y-%m-%d"),
                "修改人": User.query.filter_by(id=v.update_author_id).first().username,
                "修改日期": v.update_timestamp.strftime("%Y-%m-%d")
            })

        return data

    def post(self):
        args = self.parser.parse_args()
        import json
        print(json.dumps(args))

        method = args["method"].lower()
        if method == "create":
            return self.__create(args), 201
        elif method == "edit":
            return self.__edit(args), 201
        elif method == "delete":
            return self.__delete(args), 201
        elif method == "query":
            return self.__query(args), 201

        return {"status": "fail", "msg": "方法: %s 不支持" % method}, 201

    def __create(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        case = AutoCase.query.filter(and_(AutoCase.name == args["name"],
                                          AutoCase.suite_id == args["suite_id"])).first()
        if case is None:
            try:
                case = AutoCase(name=args["name"],
                                desc=args["desc"],
                                suite_id=args["suite_id"],
                                tags=args["tags"],
                                enable=args["enable"],
                                setup=args["setup"],
                                teardown=args["teardown"],
                                create_author_id=current_user.get_id(),
                                update_author_id=current_user.get_id())

                db.session.add(case)
                db.session.commit()
                result["suite_id"] = case.suite_id
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "异常：%s" % str(e)
        else:
            result["status"] = "fail"
            result["msg"] = "用例名称[%s]重复" % args["name"]

        return result

    def __edit(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}
        case = AutoCase.query.filter_by(id=args["id"]).first()
        if case is None:
            result["status"] = "fail"
            result["msg"] = "未找到要修改的用例id"
        else:
            try:
                case.name = args["name"]
                case.desc = args["desc"]
                case.tags = args["tags"]
                case.enable = args["enable"]
                case.setup = args["setup"]
                case.teardown = args["teardown"]

                case.update_author_id = current_user.get_id()
                case.update_timestamp = datetime.now()

                db.session.merge(case)
                db.session.commit()
                result["suite_id"] = case.suite_id
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "编辑用例[id-%s]失败：%s" % (args["id"], str(e))

        return result

    def __query(self, args):
        data = {"data": []}
        if args["id"] == -1:
            status = {True: "激活", False: "不可用"}
            projects = AutoProject.query.all()
            for p in projects:
                data["data"].append({
                    "id": p.id,
                    "名称": p.name,
                    #"所属产品": AutoProduct.query.filter_by(id=p.product_id).first().name,
                    "描述": p.desc,
                    "状态": status[p.enable],
                    "创建人": User.query.filter_by(id=p.create_author_id).first().username,
                    "创建日期": p.create_timestamp.strftime("%Y-%m-%d"),
                    "修改人": User.query.filter_by(id=p.update_author_id).first().username,
                    "修改日期": p.update_timestamp.strftime("%Y-%m-%d")
                })
        else:
            project = AutoProject.query.filter_by(id=args["id"]).first()

            return [{
                "name": project.name,
                "open": False,
                "icon": url_for("static", filename="images/project.png"),
                "attr": {
                    "category": "project",
                    "id": project.id,
                    "name": project.name
                    },
                "children": []
            }
            ]


        return data

    def __delete(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        case = AutoCase.query.filter_by(id=args["id"]).first()
        if case is None:
            result["status"] = "fail"
            result["msg"] = "未找到要删除的用例id"
        else:
            try:
                result["suite_id"] = case.suite_id
                db.session.delete(case)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "删除用例[id-%s]失败：%s" % (args["id"], str(e))

        return result
