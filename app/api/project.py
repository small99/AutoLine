# -*- coding: utf-8 -*-

__author__ = "苦叶子"

"""

公众号: 开源优测

Email: lymking@foxmail.com

"""

from datetime import datetime
from flask import url_for, current_app
from flask_restful import Resource, reqparse
from flask_login import current_user

from ..models import AutoProduct, AutoProject, AutoSuite, AutoObject, AutoCase, AutoVar, AutoStep, User
from .. import db


class Project(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('category', type=str)
        self.parser.add_argument('product_id', type=int)
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('desc', type=str)
        self.parser.add_argument('version', type=str)
        self.parser.add_argument('tags', type=str)
        self.parser.add_argument('enable', type=bool, default=True)
        self.parser.add_argument('id', type=int, default=-1)
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('cron', type=str)
        self.parser.add_argument('setup', type=str)
        self.parser.add_argument('teardown', type=str)

        self.parser.add_argument('page', type=int, default=1)
        self.parser.add_argument('rows', type=int, default=15)

    def get(self):
        args = self.parser.parse_args()
        if args["id"] == -1:

            pagination = AutoProject.query.order_by(AutoProject.id.desc()).paginate(
                args["page"], per_page=args["rows"],
                error_out=False
            )

            projects = pagination.items
            data = {"total": pagination.total, "rows": []}

            status = {True: "激活", False: "不可用"}
            for p in projects:
                data["rows"].append({
                    "id": p.id,
                    "名称": p.name,
                    "分类": p.category,
                    "product_id": p.product_id,
                    "所属产品": AutoProduct.query.filter_by(id=p.product_id).first().name,
                    "描述": p.desc,
                    "cron": p.cron,
                    "状态": status[p.enable],
                    "创建人": User.query.filter_by(id=p.create_author_id).first().username,
                    "创建日期": p.create_timestamp.strftime("%Y-%m-%d"),
                    "修改人": User.query.filter_by(id=p.update_author_id).first().username,
                    "修改日期": p.update_timestamp.strftime("%Y-%m-%d")
                })
        else:
            project = AutoProject.query.filter_by(id=args["id"]).first()
            children = []
            if project:
                # 对象集
                children.extend(self.__get_object_suites_by_project_id(project.id))
                # 套件集
                children.extend(self.__get_suites_by_project_id(project.id))

            return [{
                "id": project.id,
                "text": project.name,
                "iconCls": "icon-project",
                "attributes": {
                    "category": "project",
                    "id": project.id,
                    "name": project.name,
                    "desc": project.desc,
                    "cron": project.cron
                },
                "children": children
            }]

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

        project = AutoProduct.query.filter_by(name=args["name"]).first()
        if project is None:
            try:
                project = AutoProject(name=args["name"],
                                      desc=args["desc"],
                                      category=args["category"],
                                      product_id=args["product_id"],
                                      tags=args["tags"],
                                      enable=args["enable"],
                                      version=args["version"],
                                      cron=args["cron"],
                                      setup=args["setup"],
                                      teardown=args["teardown"],
                                      create_author_id=current_user.get_id(),
                                      update_author_id=current_user.get_id())

                db.session.add(project)
                db.session.commit()
                # app = current_app._get_current_object()
                # app.config["TRIGGER"].load_job_list()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "异常：%s" % str(e)
        else:
            result["status"] = "fail"
            result["msg"] = "项目名称[%s]重复" % args["name"]

        return result

    def __edit(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}
        project = AutoProject.query.filter_by(id=args["id"]).first()
        if project is None:
            result["status"] = "fail"
            result["msg"] = "未找到要修改的项目id"
        else:
            try:
                project.category = args["category"]
                project.product_id = args["product_id"]
                project.name = args["name"]
                project.desc = args["desc"]
                project.tags = args["tags"]
                project.enable = args["enable"]
                project.version = args["version"]
                project.cron = args["cron"]
                project.setup = args["setup"]
                project.teardown = args["teardown"]

                project.update_author_id = current_user.get_id()

                project.update_timestamp = datetime.now()

                db.session.merge(project)
                db.session.commit()

                app = current_app._get_current_object()

                app.config["TRIGGER"].update_job(args["id"])

            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "编辑项目[id-%s]失败：%s" % (args["id"], str(e))

        return result

    def __query(self, args):
        data = {"rows": []}
        if args["id"] == -1:
            status = {True: "激活", False: "不可用"}
            projects = AutoProject.query.all()
            for p in projects:
                data["rows"].append({
                    "id": p.id,
                    "名称": p.name,
                    "分类": p.category,
                    "所属产品": AutoProduct.query.filter_by(id=p.product_id).first().name,
                    "描述": p.desc,
                    "状态": status[p.enable],
                    "创建人": User.query.filter_by(id=p.create_author_id).first().username,
                    "创建日期": p.create_timestamp.strftime("%Y-%m-%d"),
                    "修改人": User.query.filter_by(id=p.update_author_id).first().username,
                    "修改日期": p.update_timestamp.strftime("%Y-%m-%d")
                })
        elif args["id"] == -2:
            # 简略信息
            projects = AutoProject.query.all()
            for p in projects:
                data["rows"].append({
                    "id": p.id,
                    "名称": p.name
                })

        return data

    def __delete(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        project = AutoProject.query.filter_by(id=args["id"]).first()
        if project is None:
            result["status"] = "fail"
            result["msg"] = "未找到要删除的项目id"
        else:
            try:
                app = current_app._get_current_object()
                app.config["TRIGGER"].remove_job(args["id"])

                db.session.delete(project)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "删除项目[id-%s]失败：%s" % (args["id"], str(e))

        return result

    def __get_suites_by_project_id(self, id):
        children = []
        suites = AutoSuite.query.filter_by(project_id=id).order_by(AutoSuite.id.asc()).all()
        for suite in suites:
            cases = self.__get_cases_by_suite_id(suite.id)
            children.append({
                "id": suite.id,
                "text": suite.name,
                "iconCls": "icon-suite",
                "attributes": {
                    "category": "suite",
                    "id": suite.id,
                    "project_id": suite.project_id,
                    "name": suite.name,
                    "desc": suite.desc
                },
                "children": cases

            })

        return children

    def __get_cases_by_suite_id(self, id):
        children = []
        cases = AutoCase.query.filter_by(suite_id=id).order_by(AutoCase.id.asc()).all()
        for case in cases:
            steps = self.__get_steps_by_case_id(case.id)
            children.append({
                "id": case.id,
                "text": case.name,
                "iconCls": "icon-case",
                "attributes": {
                    "category": "case",
                    "id": case.id,
                    "suite_id": case.suite_id,
                    "name": case.name,
                    "desc": case.desc
                },
                "children": steps})

        return children

    def __get_steps_by_case_id(self, id):
        children = []
        steps = AutoStep.query.filter_by(case_id=id).order_by(AutoStep.id.asc()).all()
        for step in steps:
            #print(step.keyword)
            children.append({
                "id": step.id,
                "text": step.keyword, #.split(".")[1],
                "iconCls": "icon-step",
                "attributes": {
                    "keyword": step.keyword,
                    "category": "step",
                    "id": step.id,
                    "case_id": step.case_id,
                    "desc": step.desc,
                    "param_1": step.param_1,
                    "param_2": step.param_2,
                    "param_3": step.param_3,
                    "param_4": step.param_4
                }})

        return children

    def __get_object_suites_by_project_id(self, id):
        children = []
        objects = AutoObject.query.filter_by(project_id=id).order_by(AutoObject.id.asc()).all()

        for obj in objects:
            vars = self.__get_var_by_object_id(obj.id)
            children.append({
                "id": obj.id,
                "text": obj.name,
                "iconCls": "icon-object",
                "attributes": {
                    "category": obj.category,
                    "id": obj.id,
                    "project_id": obj.project_id,
                    "name": obj.name,
                    "desc": obj.desc
                },
                "children": vars

            })

        return children

    def __get_var_by_object_id(self, id):
        children = []
        vars = AutoVar.query.filter_by(object_id=id).order_by(AutoVar.id.asc()).all()
        for var in vars:
            children.append({
                "id": var.id,
                "text": var.name,
                "iconCls": "icon-var",
                "attributes": {
                    "category": var.category,
                    "id": var.id,
                    "object_id": var.object_id,
                    "name": var.name,
                    "value": var.value,
                    "desc": var.desc
                }})

        return children
