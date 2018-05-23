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

from ..models import AutoSuite, AutoVar, User, AutoObject
from .. import db


class Var(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int)
        self.parser.add_argument('object_id', type=int, default=-1)
        self.parser.add_argument('desc', type=str)
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('value', type=str)
        self.parser.add_argument('category', type=str, default='var')
        self.parser.add_argument('prev', type=int)
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('page', type=int, default=1)
        self.parser.add_argument('rows', type=int, default=15)

    def get(self):
        args = self.parser.parse_args()

        pagination = AutoVar.query.filter_by(object_id=args["object_id"]).order_by(AutoVar.id.asc()).paginate(
            args["page"], per_page=args["rows"],
            error_out=False
        )

        vars = pagination.items
        data = {"total": pagination.total, "rows": []}
        for v in vars:
            data["rows"].append({
                "id": v.id,
                "object_id": v.object_id,
                "名称": v.name,
                "描述": v.desc,
                "值": v.value,
                "创建人": User.query.filter_by(id=v.create_author_id).first().username,
                "创建日期": v.create_timestamp.strftime("%Y-%m-%d"),
                "修改人": User.query.filter_by(id=v.update_author_id).first().username,
                "修改日期": v.update_timestamp.strftime("%Y-%m-%d")
            })

        return data

    def post(self):
        args = self.parser.parse_args()
        import json

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

        a_object = AutoObject.query.filter_by(id=args["object_id"]).first()
        if a_object is not None:
            project_id = a_object.project_id
            objs = AutoObject.query.filter_by(project_id=project_id).all()
            for obj in objs:
                var = AutoVar.query.filter(and_(AutoVar.name == args["name"],
                                                AutoVar.object_id == obj.id)).first()
                if var is not None:
                    result["status"] = "fail"
                    result["msg"] = "变量名[%s]重复" % args["name"]

        var = AutoVar.query.filter(and_(AutoVar.name == args["name"],
                                        AutoVar.object_id == args["object_id"])).first()

        if var is None:
            try:
                var = AutoVar(name=args["name"],
                              value=args["value"],
                              desc=args["desc"],
                              category=args['category'],
                              object_id=args["object_id"],
                              prev=args["prev"],
                              create_author_id=current_user.get_id(),
                              update_author_id=current_user.get_id())

                db.session.add(var)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "异常：%s" % str(e)
        else:
            result["status"] = "fail"
            result["msg"] = "变量名[%s]重复" % args["name"]

        return result

    def __edit(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}
        var = AutoVar.query.filter_by(id=args["id"]).first()
        if var is None:
            result["status"] = "fail"
            result["msg"] = "未找到要修改的变量id"
        else:
            try:
                var.name = args["name"]
                var.value = args["value"]
                var.desc = args["desc"]

                var.update_author_id = current_user.get_id()
                var.update_timestamp = datetime.utcnow()

                db.session.merge(var)
                db.session.commit()

            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "编辑变量[id-%s]失败：%s" % (args["id"], str(e))

        return result

    def __query(self, args):
        data = {"data": []}
        if args["id"] == -1:
            vars = AutoVar.query.all()
            for var in vars:
                data["data"].append({
                    "id": var.id,
                    "变量名": var.name,
                    "值": var.value,
                    "备注": var.desc,
                    "分类": var.category
                })
        else:
            var = AutoVar.query.filter_by(id=args["id"]).first()

            return [{
                "id": var.id,
                "text": var.name,
                "attributes": {
                    "category": var.category,
                    "id": var.id,
                    "object_id": var.object_id,
                    "name": var.name,
                    "category": var.category,
                    "value": var.value
                    }
            }
            ]

        return data

    def __delete(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        var = AutoVar.query.filter_by(id=args["id"]).first()
        if var is None:
            result["status"] = "fail"
            result["msg"] = "未找到要删除的变量id"
        else:
            try:
                db.session.delete(var)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "删除变量[id-%s]失败：%s" % (args["id"], str(e))

        return result
