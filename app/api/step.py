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

from ..models import AutoSuite, AutoCase, AutoStep, User
from .. import db


class Step(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int)
        self.parser.add_argument('case_id', type=int)
        self.parser.add_argument('prev', type=int)
        self.parser.add_argument('keyword', type=str)
        self.parser.add_argument('desc', type=str)
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('param_1', type=str)
        self.parser.add_argument('param_2', type=str)
        self.parser.add_argument('param_3', type=str)
        self.parser.add_argument('param_4', type=str)
        self.parser.add_argument('step', type=str)
        self.parser.add_argument('enable', type=bool, default=True)
        self.parser.add_argument('page', type=int, default=1)
        self.parser.add_argument('rows', type=int, default=15)

    def get(self):
        args = self.parser.parse_args()

        pagination = AutoStep.query.filter_by(case_id=args["case_id"]).order_by(AutoStep.id.asc()).paginate(
            args["page"], per_page=args["rows"],
            error_out=False
        )

        steps = pagination.items
        data = {"total": pagination.total, "rows": []}
        for v in steps:
            data["rows"].append({
                "id": v.id,
                "case_id": v.case_id,
                "关键字": v.keyword,
                "备注": v.desc,
                "参数1": v.param_1,
                "参数2": v.param_2,
                "参数3": v.param_3,
                "参数4": v.param_4,
                "创建人": User.query.filter_by(id=v.create_author_id).first().username,
                "创建日期": v.create_timestamp.strftime("%Y-%m-%d"),
                "修改人": User.query.filter_by(id=v.update_author_id).first().username,
                "修改日期": v.update_timestamp.strftime("%Y-%m-%d")
            })

        return data

    def post(self):
        args = self.parser.parse_args()
        import json
        #print(json.dumps(args))

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

        case = AutoCase.query.filter_by(id=args["case_id"]).first()
        if case is not None:
            try:
                step = AutoStep(desc=args["desc"],
                                keyword=args["keyword"],
                                case_id=args["case_id"],
                                param_1=args["param_1"],
                                param_2=args["param_2"],
                                param_3=args["param_3"],
                                param_4=args["param_4"],
                                enable=args["enable"],
                                step=args["step"],
                                prev=args["prev"],
                                create_author_id=current_user.get_id(),
                                update_author_id=current_user.get_id())

                db.session.add(step)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "异常：%s" % str(e)
        else:
            result["status"] = "fail"
            result["msg"] = "步骤id[%s]不存在" % args["name"]

        return result

    def __edit(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}
        step = AutoStep.query.filter_by(id=args["id"]).first()
        if step is None:
            result["status"] = "fail"
            result["msg"] = "未找到要修改的步骤id"
        else:
            try:
                step.desc = args["desc"]
                step.prev = args["prev"]
                step.enable = args["enable"]
                step.keyword = args["keyword"]
                step.param_1 = args["param_1"]
                step.param_2 = args["param_2"]
                step.param_3 = args["param_3"]
                step.param_4 = args["param_4"]

                step.update_author_id = current_user.get_id()
                step.update_timestamp = datetime.now()

                db.session.merge(step)
                db.session.commit()

            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "编辑步骤[id-%s]失败：%s" % (args["id"], str(e))

        return result

    """
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
    """


    def __delete(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        step = AutoStep.query.filter_by(id=args["id"]).first()
        if step is None:
            result["status"] = "fail"
            result["msg"] = "未找到要删除的步骤id"
        else:
            try:
                db.session.delete(step)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "删除步骤[id-%s]失败：%s" % (args["id"], str(e))

        return result
