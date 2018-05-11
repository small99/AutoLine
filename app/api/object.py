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

from ..models import AutoObject, AutoProject, User
from .. import db


class Object(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, default=-1)
        self.parser.add_argument('project_id', type=int)
        self.parser.add_argument('category', type=str)
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

        pagination = AutoObject.query.filter_by(project_id=args["project_id"]).order_by(AutoObject.id.asc()).paginate(
            args["page"], per_page=args["rows"],
            error_out=False
        )

        objects = pagination.items
        data = {"total": pagination.total, "rows": []}
        for o in objects:
            data["rows"].append({
                "id": o.id,
                "project_id": o.project_id,
                "名称": o.name,
                "描述": o.desc,
                "创建人": User.query.filter_by(id=o.create_author_id).first().username,
                "创建日期": o.create_timestamp.strftime("%Y-%m-%d"),
                "修改人": User.query.filter_by(id=o.update_author_id).first().username,
                "修改日期": o.update_timestamp.strftime("%Y-%m-%d")
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
        result = {"status": "success", "project_id": args["project_id"],
                  "msg": "操作成功"}

        suite = AutoObject.query.filter(and_(AutoObject.name == args["name"],
                                             AutoObject.project_id == args["project_id"])).first()
        if suite is None:
            try:
                suite = AutoObject(name=args["name"],
                                   desc=args["desc"],
                                   project_id=args["project_id"],
                                   tags=args["tags"],
                                   category=args["category"],
                                   enable=args["enable"],
                                   setup=args["setup"],
                                   teardown=args["teardown"],
                                   create_author_id=current_user.get_id(),
                                   update_author_id=current_user.get_id())

                db.session.add(suite)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "异常：%s" % str(e)
        else:
            result["status"] = "fail"
            result["msg"] = "对象集名称[%s]重复" % args["name"]

        return result

    def __edit(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}
        suite = AutoObject.query.filter_by(id=args["id"]).first()
        if suite is None:
            result["status"] = "fail"
            result["msg"] = "未找到要修改的对象集id"
        else:
            try:
                suite.name = args["name"]
                suite.desc = args["desc"]
                suite.tags = args["tags"]
                suite.enable = args["enable"]
                suite.setup = args["setup"]
                suite.teardown = args["teardown"]

                suite.update_author_id = current_user.get_id()
                suite.update_timestamp = datetime.now()

                db.session.merge(suite)
                db.session.commit()

                result["project_id"] = suite.project_id

            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "编辑对象集[id-%s]失败：%s" % (args["id"], str(e))

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

        suite = AutoObject.query.filter_by(id=args["id"]).first()
        if suite is None:
            result["status"] = "fail"
            result["msg"] = "未找到要删除的对象集id"
        else:
            try:
                result["project_id"] = suite.project_id
                db.session.delete(suite)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "删除对象集[id-%s]失败：%s" % (args["id"], str(e))

        return result
